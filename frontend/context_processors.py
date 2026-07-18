from catalogo.models import ConfiguracionNegocio


def configuracion_negocio(request):
    config = ConfiguracionNegocio.obtener()
    return {'config_negocio': config}
