from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Pago
from django.db.models.signals import pre_save
from .models import Pedido

DIAS_ENTREGA_DEFAULT = 5  # días hábiles estimados tras verificar el pago


@receiver(post_save, sender=Pago)
def actualizar_pedido_al_verificar_pago(sender, instance, **kwargs):
    if instance.estado != 'verificado':
        return

    pedido = instance.pedido
    campos_a_actualizar = []

    if pedido.estado == 'en_verificacion':
        pedido.estado = 'confirmado'
        campos_a_actualizar.append('estado')

    if not pedido.fecha_estimada_entrega:
        pedido.fecha_estimada_entrega = timezone.now().date() + timedelta(days=DIAS_ENTREGA_DEFAULT)
        campos_a_actualizar.append('fecha_estimada_entrega')

    if campos_a_actualizar:
        pedido.save(update_fields=campos_a_actualizar)

@receiver(pre_save, sender=Pedido)
def marcar_notificacion_al_entregar(sender, instance, **kwargs):
    if not instance.pk:
        return  # pedido nuevo, todavía no tiene estado anterior que comparar
    try:
        anterior = Pedido.objects.get(pk=instance.pk)
    except Pedido.DoesNotExist:
        return
    if anterior.estado != 'entregado' and instance.estado == 'entregado':
        instance.notificacion_entrega_pendiente = True