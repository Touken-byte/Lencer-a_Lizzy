import django_filters
from .models import Producto


class ProductoFilter(django_filters.FilterSet):
    """
    HU-02: filtrar por subcategoría -> ?subcategoria=<id>
    HU-06: filtrar por talla y/o color -> ?talla=M&color=negro
    Todos los filtros son combinables entre sí (AND).
    """
    categoria = django_filters.NumberFilter(field_name='categoria__id')
    subcategoria = django_filters.NumberFilter(field_name='subcategoria__id')
    talla = django_filters.CharFilter(field_name='talla', lookup_expr='iexact')
    color = django_filters.CharFilter(field_name='color', lookup_expr='icontains')
    en_oferta = django_filters.BooleanFilter(field_name='en_oferta')

    class Meta:
        model = Producto
        fields = ['categoria', 'subcategoria', 'talla', 'color', 'en_oferta']