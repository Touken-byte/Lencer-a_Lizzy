from django.contrib import admin
from .models import Pedido, ItemPedido, Pago


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('subtotal',)


class PagoInline(admin.StackedInline):
    model = Pago
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'clienta', 'estado', 'tipo_entrega', 'total', 'creado')
    list_filter = ('estado', 'tipo_entrega')
    list_editable = ('estado',)
    inlines = [ItemPedidoInline, PagoInline]
    readonly_fields = ('total', 'creado', 'actualizado')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'metodo', 'estado', 'saldo_pendiente')
    list_filter = ('metodo', 'estado')
    actions = ['marcar_verificado', 'marcar_rechazado']

    @admin.action(description='Marcar como VERIFICADO')
    def marcar_verificado(self, request, queryset):
        queryset.update(estado='verificado')

    @admin.action(description='Marcar como RECHAZADO')
    def marcar_rechazado(self, request, queryset):
        queryset.update(estado='rechazado')
