from django.contrib import admin
from .forms import ProductoForm
from .models import Categoria, Subcategoria, Producto, ImagenProducto, ConfiguracionNegocio
from django import forms
from django.core.exceptions import ValidationError


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden')
    ordering = ('orden',)


@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria')
    list_filter = ('categoria',)

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
    extra = 2
    fields = ('imagen', 'orden', 'es_portada')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoForm
    list_display = (
        'nombre', 'categoria', 'subcategoria', 'talla', 'color',
        'precio', 'precio_final_display', 'stock', 'estado_display', 'en_oferta',
    )
    list_filter = ('categoria', 'subcategoria', 'talla', 'agotado', 'activo', 'en_oferta')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'stock')
    inlines = [ImagenProductoInline]

    fieldsets = (
        ('Información general', {
            'fields': ('nombre', 'descripcion', 'categoria', 'subcategoria', 'color', 'talla')
        }),
        ('Precio y stock', {
            'fields': ('precio', 'stock')
        }),
        ('Disponibilidad (HU-30)', {
            'fields': ('agotado', 'activo')
        }),
        ('Oferta y descuento (HU-31)', {
            'fields': ('en_oferta', 'porcentaje_descuento')
        }),
    )

    actions = ['marcar_agotado', 'marcar_disponible', 'desactivar_producto']

    @admin.display(description='Precio final')
    def precio_final_display(self, obj):
        return f"Bs {obj.precio_final}"

    @admin.display(description='Estado')
    def estado_display(self, obj):
        if not obj.activo:
            return "Eliminado"
        if obj.agotado:
            return "Agotado"
        return "Disponible"

    @admin.action(description='Marcar seleccionados como AGOTADO')
    def marcar_agotado(self, request, queryset):
        queryset.update(agotado=True)

    @admin.action(description='Marcar seleccionados como DISPONIBLE')
    def marcar_disponible(self, request, queryset):
        queryset.update(agotado=False)

    @admin.action(description='Eliminar (desactivar) productos seleccionados')
    def desactivar_producto(self, request, queryset):
        queryset.update(activo=False)


@admin.register(ConfiguracionNegocio)
class ConfiguracionNegocioAdmin(admin.ModelAdmin):
    list_display = ('nombre_negocio', 'whatsapp_numero', 'monto_minimo_apartado')

    fieldsets = (
        ('Datos del negocio', {
            'fields': ('nombre_negocio', 'whatsapp_numero')
        }),
        ('Datos bancarios (HU-40)', {
            'fields': ('banco_nombre', 'banco_titular', 'banco_numero_cuenta', 'qr_pago')
        }),
        ('Apartados (HU-37)', {
            'fields': ('monto_minimo_apartado',)
        }),
        ('Ubicación del local', {
            'fields': ('direccion_local', 'mapa_url', 'foto_local')
        }),
    )

    def has_add_permission(self, request):
        # Singleton: si ya existe una configuración, no permitir crear otra
        return not ConfiguracionNegocio.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
