from catalogo.models import ConfiguracionNegocio
from django.utils import timezone
from django.conf import settings


def configuracion_negocio(request):
    config = ConfiguracionNegocio.obtener()
    context = {
        'config_negocio': config,
        'contacto_privacidad_email': settings.CONTACTO_PRIVACIDAD_EMAIL,
        'demo_usuario': settings.DEMO_USUARIO,
        'demo_password': settings.DEMO_PASSWORD,
        'es_demo': request.user.is_authenticated and request.user.username == settings.DEMO_USUARIO,
    }

    if request.user.is_authenticated and not request.user.is_staff:
        from pedidos.models import Pedido
        from datetime import timedelta
        hoy = timezone.now().date()
        hay_atraso = Pedido.objects.filter(
            clienta=request.user,
            fecha_estimada_entrega__lte=hoy + timedelta(days=1),
        ).exclude(estado__in=['entregado', 'cancelado']).exists()
        hay_entrega_sin_ver = Pedido.objects.filter(
            clienta=request.user, notificacion_entrega_pendiente=True
        ).exists()
        context['hay_alerta_pedidos'] = hay_atraso or hay_entrega_sin_ver
        from chat.models import Mensaje
        context['chat_sin_leer'] = Mensaje.objects.filter(
            usuario=request.user, emisor='vendedora', leido=False
        ).count()

    return context