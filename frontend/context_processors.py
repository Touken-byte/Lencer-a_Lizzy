from catalogo.models import ConfiguracionNegocio
from django.utils import timezone


def configuracion_negocio(request):
    config = ConfiguracionNegocio.obtener()
    context = {'config_negocio': config}

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

    return context