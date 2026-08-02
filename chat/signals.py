from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from pedidos.models import Pedido
from .models import Mensaje

_estado_anterior = {}


@receiver(pre_save, sender=Pedido)
def guardar_estado_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            anterior = Pedido.objects.get(pk=instance.pk)
            _estado_anterior[instance.pk] = anterior.estado
        except Pedido.DoesNotExist:
            _estado_anterior[instance.pk] = None


@receiver(post_save, sender=Pedido)
def notificar_cambio_estado(sender, instance, created, **kwargs):
    if created:
        return
    anterior = _estado_anterior.get(instance.pk)
    if anterior and anterior != instance.estado:
        primer_item = instance.items.first()
        producto_nombre = primer_item.producto.nombre if primer_item else "tu pedido"
        Mensaje.objects.create(
            usuario=instance.clienta,
            emisor='vendedora',
            texto=f"Tu pedido #{instance.id} ({producto_nombre}) cambió de estado: {instance.get_estado_display()}.",
            automatico=True,
        )
