from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from catalogo.models import Producto
from clientas.models import DireccionEntrega


class Pedido(models.Model):
    """HU-08, HU-09, HU-21, HU-22, HU-23, HU-32, HU-33"""

    ESTADO_CHOICES = [
        ('confirmado', 'Confirmado'),
        ('preparacion', 'En preparación'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    ENTREGA_CHOICES = [
        ('domicilio', 'Envío a domicilio'),
        ('recogida', 'Recogida en punto físico'),
    ]

    clienta = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pedidos')
    direccion = models.ForeignKey(
        DireccionEntrega, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos'
    )
    tipo_entrega = models.CharField(max_length=15, choices=ENTREGA_CHOICES, default='domicilio')

    nota = models.CharField(max_length=300, blank=True, help_text="HU-09: nota para la vendedora")

    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='confirmado')
    fecha_estimada_entrega = models.DateField(null=True, blank=True)

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-creado']

    def __str__(self):
        return f"Pedido #{self.pk} - {self.clienta.username}"

    def recalcular_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total = total
        self.save(update_fields=['total'])


class ItemPedido(models.Model):
    """HU-07, HU-08: productos dentro del carrito/pedido"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='items_pedido')
    talla = models.CharField(max_length=10)
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = "Ítem de pedido"
        verbose_name_plural = "Ítems de pedido"

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} ({self.talla})"

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad


class Pago(models.Model):
    """HU-11 a HU-15, HU-34, HU-35: métodos de pago y verificación"""

    METODO_CHOICES = [
        ('qr', 'Pago con QR'),
        ('transferencia', 'Transferencia bancaria'),
        ('efectivo', 'Efectivo al recibir'),
        ('whatsapp', 'Coordinar por WhatsApp (pago presencial)'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de verificación'),
        ('verificado', 'Verificado'),
        ('rechazado', 'Rechazado'),
    ]

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='pago')
    metodo = models.CharField(max_length=15, choices=METODO_CHOICES)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')

    comprobante = models.ImageField(upload_to='comprobantes/%Y/%m/', blank=True, null=True)

    # HU-14: apartado / cuotas
    monto_apartado = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    saldo_pendiente = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"Pago #{self.pk} - {self.get_metodo_display()} - {self.pedido}"
