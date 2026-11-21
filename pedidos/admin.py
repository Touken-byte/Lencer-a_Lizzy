from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Pedido, ItemPedido, Pago


class ItemPedidoInlineForm(forms.ModelForm):
    """Si no se escribe el precio, se usa el precio final del producto."""
    class Meta:
        model = ItemPedido
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['precio_unitario'].required = False

    def clean(self):
        datos = super().clean()
        producto = datos.get('producto')
        if producto and datos.get('precio_unitario') in (None, ''):
            datos['precio_unitario'] = producto.precio_final
        return datos


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    form = ItemPedidoInlineForm
    extra = 3
    readonly_fields = ('subtotal',)


class PagoInline(admin.StackedInline):
    model = Pago
    extra = 1
    max_num = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'clienta', 'estado', 'tipo_entrega',
        'metodo_pago_display', 'estado_pago_display', 'nombre_referencia_display',
        'fecha_estimada_entrega', 'alerta_display', 'total', 'fecha_venta', 'lugar_venta', 'origen', 'creado',
    )
    list_filter = ('estado', 'tipo_entrega', 'origen', 'lugar_venta')
    list_editable = ('estado', 'fecha_estimada_entrega')
    inlines = [ItemPedidoInline, PagoInline]
    readonly_fields = ('total', 'creado', 'actualizado')
    actions = [
        'verificar_pago_seleccionados',
        'rechazar_pago_seleccionados',
        'marcar_entregado_seleccionados',
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and obj.origen != 'estimado' and (
            'estado' in form.changed_data or 'fecha_estimada_entrega' in form.changed_data
        ):
            Pedido.objects.filter(pk=obj.pk).update(notificacion_entrega_pendiente=True)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        pedido = form.instance
        for fs in formsets:
            if fs.model is Pago and pedido.origen != 'estimado' and any(
                'estado' in f.changed_data for f in fs.forms
            ):
                Pedido.objects.filter(pk=pedido.pk).update(notificacion_entrega_pendiente=True)
        if pedido.origen == 'estimado':
            pago = Pago.objects.filter(pedido=pedido).first()
            if pago is None:
                # Venta en feria sin otro método indicado: efectivo ya cobrado
                Pago.objects.create(pedido=pedido, metodo='efectivo', estado='verificado')
            elif pago.estado == 'pendiente':
                pago.estado = 'verificado'
                pago.save()
        pedido.recalcular_total()

    @admin.display(description='Método de pago')
    def metodo_pago_display(self, obj):
        pago = getattr(obj, 'pago', None)
        return pago.get_metodo_display() if pago else '—'

    @admin.display(description='Estado del pago')
    def estado_pago_display(self, obj):
        pago = getattr(obj, 'pago', None)
        if not pago:
            return '—'
        color = {'verificado': '#198754', 'pendiente': '#ffc107', 'rechazado': '#dc3545'}.get(pago.estado, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 10px;border-radius:10px;">{}</span>',
            color, pago.get_estado_display()
        )

    @admin.display(description='Referencia de pago')
    def nombre_referencia_display(self, obj):
        pago = getattr(obj, 'pago', None)
        return pago.nombre_referencia if pago and pago.nombre_referencia else '—'

    @admin.display(description='Alerta')
    def alerta_display(self, obj):
        if obj.alerta_atraso:
            return format_html(
                '<span style="background:#dc3545;color:white;padding:2px 10px;border-radius:10px;">{}</span>',
                '⚠ Atraso'
            )
        return '—'

    @admin.action(description='✅ Verificar pago de los pedidos seleccionados')
    def verificar_pago_seleccionados(self, request, queryset):
        actualizados = 0
        for pedido in queryset:
            pago = getattr(pedido, 'pago', None)
            if pago and pago.estado != 'verificado':
                pago.estado = 'verificado'
                pago.save()
                Pedido.objects.filter(pk=pedido.pk).update(notificacion_entrega_pendiente=True)
                actualizados += 1
        self.message_user(request, f"{actualizados} pago(s) marcado(s) como verificado.")

    @admin.action(description='❌ Rechazar pago de los pedidos seleccionados')
    def rechazar_pago_seleccionados(self, request, queryset):
        actualizados = 0
        for pedido in queryset:
            pago = getattr(pedido, 'pago', None)
            if pago and pago.estado != 'rechazado':
                pago.estado = 'rechazado'
                pago.save()
                Pedido.objects.filter(pk=pedido.pk).update(notificacion_entrega_pendiente=True)
                actualizados += 1
        self.message_user(request, f"{actualizados} pago(s) marcado(s) como rechazado.")

    @admin.action(description='📦 Marcar como ENTREGADO los pedidos seleccionados')
    def marcar_entregado_seleccionados(self, request, queryset):
        actualizados = 0
        for pedido in queryset:
            if pedido.estado != 'entregado':
                pedido.estado = 'entregado'
                pedido.notificacion_entrega_pendiente = True
                pedido.save(update_fields=['estado', 'notificacion_entrega_pendiente'])
                actualizados += 1
        self.message_user(request, f"{actualizados} pedido(s) marcado(s) como entregado.")

    class Media:
        css = {'all': ('css/pedido_admin.css',)}


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'metodo', 'nombre_referencia', 'estado')
    list_filter = ('metodo', 'estado')
    actions = ['marcar_verificado', 'marcar_rechazado']

    def has_module_permission(self, request):
        # Oculta "Pagos" del menú lateral: se edita siempre desde dentro de Pedidos (PagoInline)
        return False

    @admin.action(description='Marcar como VERIFICADO')
    def marcar_verificado(self, request, queryset):
        queryset.update(estado='verificado')

    @admin.action(description='Marcar como RECHAZADO')
    def marcar_rechazado(self, request, queryset):
        queryset.update(estado='rechazado')