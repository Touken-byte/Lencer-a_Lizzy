from django.contrib import admin
from .models import Pedido, ItemPedido, Pago


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('subtotal',)


class PagoInline(admin.StackedInline):
    model = Pago
    extra = 0


from django.utils.html import format_html


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'clienta', 'estado', 'tipo_entrega',
        'metodo_pago_display', 'estado_pago_display', 'nombre_referencia_display',
        'fecha_estimada_entrega', 'alerta_display', 'total', 'creado',
    )
    list_filter = ('estado', 'tipo_entrega')
    list_editable = ('estado', 'fecha_estimada_entrega')
    inlines = [ItemPedidoInline, PagoInline]
    readonly_fields = ('total', 'creado', 'actualizado')
    actions = ['verificar_pago_seleccionados', 'rechazar_pago_seleccionados']

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
                actualizados += 1
        self.message_user(request, f"{actualizados} pago(s) marcado(s) como rechazado.")@admin.action(description='✅ Verificar pago de los pedidos seleccionados')

    def verificar_pago_seleccionados(self, request, queryset):
        actualizados = 0
        for pedido in queryset:
            pago = getattr(pedido, 'pago', None)
            if pago and pago.estado != 'verificado':
                pago.estado = 'verificado'
                pago.save()
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
                actualizados += 1
        self.message_user(request, f"{actualizados} pago(s) marcado(s) como rechazado.")


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