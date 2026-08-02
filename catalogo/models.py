from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Categoria(models.Model):
    """Mujer, Hombre, Otros (HU-01)"""
    nombre = models.CharField(max_length=50, unique=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class Subcategoria(models.Model):
    """Arriba, abajo, medias, accesorios (HU-02)"""

    TIPO_TALLA_CHOICES = [
        ('letra', 'Letra (XS, S, M, L, XL, XXL)'),
        ('brassiere', 'Brasier (Banda + Copa, ej: 75B)'),
    ]

    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    nombre = models.CharField(max_length=50)
    tipo_talla = models.CharField(
        max_length=10, choices=TIPO_TALLA_CHOICES, default='letra',
        help_text="Define qué sistema de tallas usan los productos de esta subcategoría"
    )

    class Meta:
        verbose_name = "Subcategoría"
        verbose_name_plural = "Subcategorías"
        unique_together = ('categoria', 'nombre')

    def __str__(self):
        return f"{self.categoria.nombre} - {self.nombre}"


class Producto(models.Model):
    """HU-28, HU-29, HU-30, HU-31"""

    TALLA_LETRA_VALORES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'UNICA']
    TALLA_BRASSIERE_VALORES = [
        '70A', '70B', '70C', '75A', '75B', '75C',
        '80A', '80B', '80C', '85A', '85B', '85C',
    ]
    TALLA_CHOICES = [
        ('Letra', [(v, v if v != 'UNICA' else 'Única') for v in TALLA_LETRA_VALORES]),
        ('Brasier (Banda + Copa)', [(v, v) for v in TALLA_BRASSIERE_VALORES]),
    ]

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.PROTECT, related_name='productos')

    precio = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    activo = models.BooleanField(default=True)  # "eliminar" lógico, no físico

    # HU-31: ofertas y descuentos
    en_oferta = models.BooleanField(default=False)
    porcentaje_descuento = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(90)],
        help_text="Porcentaje de descuento (0-90)"
    )

    TEMPORADA_CHOICES = [
        ('todo_el_anio', 'Todo el año'),
        ('invierno', 'Invierno'),
        ('verano', 'Verano'),
    ]
    temporada = models.CharField(max_length=15, choices=TEMPORADA_CHOICES, default='todo_el_anio')

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-creado']

    def __str__(self):
        return self.nombre

    @property
    def precio_final(self):
        from decimal import Decimal
        if self.en_oferta and self.porcentaje_descuento > 0:
            descuento = self.precio * (Decimal(self.porcentaje_descuento) / Decimal(100))
            return round(self.precio - descuento, 2)
        return self.precio

    @property
    def es_nuevo(self):
        from django.utils import timezone
        from datetime import timedelta
        return self.creado >= timezone.now() - timedelta(days=7)

    @property
    def imagen_portada(self):
        return self.imagenes.filter(es_portada=True).first() or self.imagenes.first()

    @property
    def stock_total(self):
        """Suma el stock de todas las variantes (tallas x colores)"""
        return sum(v.stock for v in self.variantes.all())

    @property
    def agotado(self):
        return self.stock_total == 0

    @property
    def tallas_disponibles(self):
        return self.variantes.filter(stock__gt=0).values_list('talla', flat=True).distinct()

    @property
    def colores_disponibles(self):
        return self.variantes.filter(stock__gt=0).exclude(color='').values_list('color', flat=True).distinct()

    @property
    def variantes_ordenadas(self):
        """Variantes ordenadas por talla real (XS-S-M-L-XL-XXL), no alfabéticamente"""
        orden = self.TALLA_LETRA_VALORES + self.TALLA_BRASSIERE_VALORES
        return sorted(
            self.variantes.all(),
            key=lambda v: (orden.index(v.talla) if v.talla in orden else 999, v.color)
        )
    def clean(self):
        errors = {}
        if self.subcategoria_id and self.categoria_id and self.subcategoria.categoria_id != self.categoria_id:
            errors['subcategoria'] = 'La subcategoría no pertenece a la categoría seleccionada.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class VarianteProducto(models.Model):
    """Una combinación específica de talla + color con su propio stock (punto 7)"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='variantes')
    talla = models.CharField(max_length=10, choices=Producto.TALLA_CHOICES)
    color = models.CharField(max_length=50, blank=True, help_text="Déjalo vacío si el producto no maneja color")
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Variante de producto"
        verbose_name_plural = "Variantes de producto"
        ordering = ['talla', 'color']

    def __str__(self):
        color_txt = f" - {self.color}" if self.color else ""
        return f"{self.talla}{color_txt} ({self.stock} unid.)"

    @property
    def agotada(self):
        return self.stock == 0

    def clean(self):
        errors = {}
        if self.producto_id and self.talla:
            tipo = self.producto.subcategoria.tipo_talla
            if tipo == 'brassiere' and self.talla not in Producto.TALLA_BRASSIERE_VALORES:
                errors['talla'] = 'Esta subcategoría requiere una talla de brasier (ej: 75B).'
            elif tipo == 'letra' and self.talla not in Producto.TALLA_LETRA_VALORES:
                errors['talla'] = 'Esta subcategoría requiere una talla estándar (XS, S, M, L, XL, XXL).'
        if ',' in self.color:
            errors['color'] = 'Escribe un solo color por fila. Si el producto tiene varios colores, agrega una fila (variante) por cada uno.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Normaliza espacios y mayúsculas para que "Rosado" y " rosado " se traten igual
        self.color = self.color.strip()
        self.full_clean()

        # Si ya existe otra fila con la misma talla+color, le sumamos el stock
        # en vez de crear un duplicado o dar error
        existente = VarianteProducto.objects.filter(
            producto_id=self.producto_id, talla=self.talla, color__iexact=self.color
        ).exclude(pk=self.pk).first()

        if existente:
            existente.stock += self.stock
            existente.save(update_fields=['stock'])
            if self.pk:
                # Esta fila ya existía con otros datos y ahora quedó redundante: se elimina
                self.delete()
            return  # no guardamos esta fila como nueva, ya se fusionó

        super().save(*args, **kwargs)


class ImagenProducto(models.Model):
    """HU-28: mínimo 2 fotos por producto"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/%Y/%m/')
    orden = models.PositiveSmallIntegerField(default=0)
    es_portada = models.BooleanField(default=False, help_text="Imagen principal mostrada en el catálogo")

    class Meta:
        verbose_name = "Imagen de producto"
        verbose_name_plural = "Imágenes de producto"
        ordering = ['-es_portada', 'orden']

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"

    def save(self, *args, **kwargs):
        if self.es_portada:
            ImagenProducto.objects.filter(
                producto=self.producto, es_portada=True
            ).exclude(pk=self.pk).update(es_portada=False)
        super().save(*args, **kwargs)


class ConfiguracionNegocio(models.Model):
    """HU-37 y HU-40 — configuración general (singleton: una sola fila)"""

    direccion_local = models.CharField(max_length=255, blank=True, help_text="Dirección física de la tienda")
    mapa_url = models.URLField(blank=True, help_text="Link de Google Maps al local")
    foto_local = models.ImageField(upload_to='local/', blank=True, null=True)
    nombre_negocio = models.CharField(max_length=100, default="Mi Tienda")
    whatsapp_numero = models.CharField(max_length=20, help_text="Con código de país, ej: 59171234567")
    banco_nombre = models.CharField(max_length=100, blank=True)
    banco_titular = models.CharField(max_length=100, blank=True)
    banco_numero_cuenta = models.CharField(max_length=50, blank=True)
    qr_pago = models.ImageField(upload_to='configuracion/', blank=True, null=True)

    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración del negocio"
        verbose_name_plural = "Configuración del negocio"

    def __str__(self):
        return self.nombre_negocio

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def obtener(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj