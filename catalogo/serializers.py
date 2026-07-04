from rest_framework import serializers
from .models import Categoria, Subcategoria, Producto, ImagenProducto


class SubcategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategoria
        fields = ['id', 'nombre']


class CategoriaSerializer(serializers.ModelSerializer):
    """HU-01: secciones con sus subcategorías"""
    subcategorias = SubcategoriaSerializer(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'orden', 'subcategorias']


class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ['id', 'imagen', 'orden']


class ProductoListaSerializer(serializers.ModelSerializer):
    """Para listados/catálogo: info resumida (HU-01, HU-02, HU-03, HU-05, HU-06)"""
    imagen_principal = serializers.SerializerMethodField()
    precio_final = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    estado_stock = serializers.SerializerMethodField()
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    subcategoria_nombre = serializers.CharField(source='subcategoria.nombre', read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'categoria_nombre', 'subcategoria_nombre',
            'color', 'talla', 'precio', 'precio_final', 'stock',
            'estado_stock', 'en_oferta', 'porcentaje_descuento', 'imagen_principal',
        ]

    def get_imagen_principal(self, obj):
        primera = obj.imagenes.order_by('orden').first()
        if primera and primera.imagen:
            request = self.context.get('request')
            url = primera.imagen.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_estado_stock(self, obj):
        """HU-05: indicador de stock"""
        if obj.agotado or obj.stock == 0:
            return 'agotado'
        if obj.stock <= 3:
            return 'ultimas_unidades'
        return 'disponible'


class ProductoDetalleSerializer(serializers.ModelSerializer):
    """HU-04: detalle completo del producto"""
    imagenes = ImagenProductoSerializer(many=True, read_only=True)
    precio_final = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    estado_stock = serializers.SerializerMethodField()
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    subcategoria_nombre = serializers.CharField(source='subcategoria.nombre', read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'categoria_nombre', 'subcategoria_nombre',
            'color', 'talla', 'precio', 'precio_final', 'stock', 'estado_stock',
            'en_oferta', 'porcentaje_descuento', 'imagenes',
        ]

    def get_estado_stock(self, obj):
        if obj.agotado or obj.stock == 0:
            return 'agotado'
        if obj.stock <= 3:
            return 'ultimas_unidades'
        return 'disponible'