from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from catalogo.models import Producto
from clientas.models import DireccionEntrega
from django.core.exceptions import ValidationError
from django.utils import timezone

def validar_fecha_futura(value):
    if value < timezone.localtime(timezone.now()).date():
        raise ValidationError("La fecha estimada de entrega no puede ser anterior a hoy.")

class Pedido(models.Model):
    """HU-08, HU-09, HU-21, HU-22, HU-23, HU-32, HU-33"""

    ESTADO_CHOICES = [
        ('en_verificacion', 'En verificación de pago'),
        ('confirmado', 'Confirmado'),
        ('preparacion', 'En preparación'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    ENTREGA_CHOICES = [
        ('recogida', 'Recogida en punto físico'),
        ('tienda', 'Recogida en tienda física'),
    ]

    clienta = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pedidos')
    direccion = models.ForeignKey(
        DireccionEntrega, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos'
    )
    tipo_entrega = models.CharField(max_length=15, choices=ENTREGA_CHOICES, default='recogida')

    nota = models.CharField(max_length=300, blank=True, help_text="HU-09: nota para la vendedora")

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='en_verificacion')
    fecha_estimada_entrega = models.DateField(
        null=True, blank=True, validators=[validar_fecha_futura]
    )
    notificacion_entrega_pendiente = models.BooleanField(
        default=False,
        help_text="True cuando se marca como 'Entregado' y la clienta aún no ha visto el aviso"
    )

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

    def clean(self):
        if self.fecha_estimada_entrega:
            pago = getattr(self, 'pago', None)
            if not pago or pago.estado != 'verificado':
                raise ValidationError({
                    'fecha_estimada_entrega': 'No puedes poner una fecha de entrega hasta que el Pago esté marcado como "Verificado".'
                })

    @property
    def alerta_atraso(self):
        """True desde 1 día antes de la fecha estimada, mientras el pedido siga activo (punto 15)"""
        from django.utils import timezone
        from datetime import timedelta
        if self.estado in ('entregado', 'cancelado'):
            return False
        if not self.fecha_estimada_entrega:
            return False
        return self.fecha_estimada_entrega <= timezone.localtime(timezone.now()).date() + timedelta(days=1)


class ItemPedido(models.Model):
    """HU-07, HU-08: productos dentro del carrito/pedido"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='items_pedido')
    talla = models.CharField(max_length=10)
    color = models.CharField(max_length=50, blank=True)
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = "Ítem de pedido"
        verbose_name_plural = "Ítems de pedido"

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} ({self.talla})"

    @property
    def subtotal(self):
        if self.precio_unitario is None or self.cantidad is None:
            return 0
        return self.precio_unitario * self.cantidad


class Pago(models.Model):
    """HU-11 a HU-15, HU-34, HU-35: métodos de pago y verificación"""

    METODO_CHOICES = [
        ('qr', 'Pago con QR'),
        ('efectivo', 'Efectivo (presencial)'),
        ('whatsapp', 'Coordinar por WhatsApp'),
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
    nombre_referencia = models.CharField(
        max_length=100, blank=True,
        help_text="Nombre con el que la clienta hizo el pago, para identificarlo manualmente"
    )

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"Pago #{self.pk} - {self.get_metodo_display()} - {self.pedido}"