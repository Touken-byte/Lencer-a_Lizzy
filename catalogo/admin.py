from django.contrib import admin
from .forms import ProductoForm
from .models import Categoria, Subcategoria, Producto, VarianteProducto, ImagenProducto, ConfiguracionNegocio
from django import forms
from django.core.exceptions import ValidationError


class SubcategoriaInline(admin.TabularInline):
    model = Subcategoria
    extra = 1
    fields = ('nombre', 'tipo_talla')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden')
    ordering = ('orden',)
    change_form_template = 'admin/catalogo/categoria_change_form.html'
    inlines = [SubcategoriaInline]


@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'tipo_talla')
    list_filter = ('categoria', 'tipo_talla')


class ImagenProductoFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        portadas = 0
        total = 0
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if form.cleaned_data.get('DELETE'):
                continue
            if form.cleaned_data.get('imagen') or form.instance.pk:
                total += 1
                if form.cleaned_data.get('es_portada'):
                    portadas += 1
        if portadas > 1:
            raise ValidationError("Solo puede haber UNA imagen marcada como portada.")
        if total > 0 and portadas == 0:
            raise ValidationError("Debes marcar una imagen como portada.")


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    formset = ImagenProductoFormSet
    fields = ('imagen', 'orden', 'es_portada')

    def get_extra(self, request, obj=None, **kwargs):
        return 2 if obj is None else 0


class VarianteProductoInline(admin.TabularInline):
    """Aquí marcas cada talla/color disponible y cuántas unidades hay (punto 7)"""
    model = VarianteProducto
    fields = ('talla', 'color', 'stock')

    def get_extra(self, request, obj=None, **kwargs):
        return 4 if obj is None else 1

    def get_queryset(self, request):
        from django.db.models import Case, When, Value, IntegerField
        qs = super().get_queryset(request)
        orden = Producto.TALLA_LETRA_VALORES + Producto.TALLA_BRASSIERE_VALORES
        whens = [When(talla=t, then=Value(i)) for i, t in enumerate(orden)]
        qs = qs.annotate(
            orden_talla=Case(*whens, default=Value(999), output_field=IntegerField())
        )
        return qs.order_by('orden_talla', 'color')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoForm
    list_display = (
        'nombre', 'categoria', 'subcategoria',
        'precio', 'precio_final_display', 'tallas_texto', 'stock_total', 'estado_display', 'en_oferta',
    )
    list_filter = ('categoria', 'subcategoria', 'activo', 'en_oferta')
    search_fields = ('nombre', 'descripcion')
    inlines = [VarianteProductoInline, ImagenProductoInline]

    fieldsets = (
        ('Información general', {
            'fields': ('nombre', 'descripcion', 'categoria', 'subcategoria')
        }),
        ('Precio', {
            'fields': ('precio',)
        }),
        ('Disponibilidad', {
            'fields': ('activo',),
            'description': 'El stock, tallas y colores se manejan abajo, en "Variantes de producto".'
        }),
        ('Temporada', {
            'fields': ('temporada',)
        }),
        ('Oferta y descuento (HU-31)', {
            'fields': ('en_oferta', 'porcentaje_descuento')
        }),
    )

    actions = ['desactivar_producto']

    @admin.display(description='Precio final')
    def precio_final_display(self, obj):
        return f"Bs {obj.precio_final}"

    @admin.display(description='Tallas')
    def tallas_texto(self, obj):
        tallas = sorted(set(obj.variantes.values_list('talla', flat=True)))
        return ", ".join(tallas) if tallas else "— (agrega variantes abajo)"

    @admin.display(description='Stock total')
    def stock_total(self, obj):
        return obj.stock_total

    @admin.display(description='Estado')
    def estado_display(self, obj):
        if not obj.activo:
            return "Eliminado"
        if obj.agotado:
            return "Agotado"
        return "Disponible"

    @admin.action(description='Eliminar (desactivar) productos seleccionados')
    def desactivar_producto(self, request, queryset):
        queryset.update(activo=False)

    class Media:
        js = ('js/producto_admin.js',)


@admin.register(ConfiguracionNegocio)
class ConfiguracionNegocioAdmin(admin.ModelAdmin):
    list_display = ('nombre_negocio', 'whatsapp_numero')

    fieldsets = (
        ('Datos del negocio', {
            'fields': ('nombre_negocio', 'whatsapp_numero')
        }),
        ('Datos bancarios (HU-40)', {
            'fields': ('banco_nombre', 'banco_titular', 'banco_numero_cuenta', 'qr_pago')
        }),
        ('Ubicación del local', {
            'fields': ('direccion_local', 'mapa_url', 'foto_local')
        }),
    )

    def has_add_permission(self, request):
        return not ConfiguracionNegocio.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False