from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Categoria, Producto, ConfiguracionNegocio
from .serializers import CategoriaSerializer, ProductoListaSerializer, ProductoDetalleSerializer
from .filters import ProductoFilter


class CategoriaListaView(generics.ListAPIView):
    """HU-01: ver catálogo por sección, cada una con sus subcategorías"""
    queryset = Categoria.objects.prefetch_related('subcategorias').all()
    serializer_class = CategoriaSerializer


class ProductoListaView(generics.ListAPIView):
    """
    HU-02: filtrar por subcategoría (?subcategoria=<id>)
    HU-03: buscar por nombre (?search=texto)
    HU-06: filtrar por talla y color (?talla=M&color=negro)
    """
    queryset = Producto.objects.filter(activo=True).select_related(
        'categoria', 'subcategoria'
    ).prefetch_related('imagenes')
    serializer_class = ProductoListaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductoFilter
    search_fields = ['nombre', 'descripcion']

    def get_serializer_context(self):
        return {'request': self.request}


class ProductoDetalleView(generics.RetrieveAPIView):
    """HU-04: ver detalle del producto"""
    queryset = Producto.objects.filter(activo=True).prefetch_related('imagenes')
    serializer_class = ProductoDetalleSerializer

    def get_serializer_context(self):
        return {'request': self.request}


@api_view(['GET'])
@permission_classes([AllowAny])
def whatsapp_contacto(request):
    """HU-17: devuelve el número de WhatsApp y un mensaje predefinido"""
    config = ConfiguracionNegocio.obtener()
    numero = config.whatsapp_numero or ''
    mensaje = f"Hola, me comunico desde la app de {config.nombre_negocio}. Quisiera hacer una consulta."
    return Response({
        'numero': numero,
        'mensaje_predefinido': mensaje,
        'link': f"https://wa.me/{numero}?text={mensaje}" if numero else None
    })