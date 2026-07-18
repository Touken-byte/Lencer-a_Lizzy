from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Subcategoría"
        verbose_name_plural = "Subcategorías"
        unique_together = ('categoria', 'nombre')

    def __str__(self):
        return f"{self.categoria.nombre} - {self.nombre}"


class Producto(models.Model):
    """HU-28, HU-29, HU-30, HU-31"""

    TALLA_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('UNICA', 'Única'),
    ]

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.PROTECT, related_name='productos')
    color = models.CharField(max_length=50, blank=True)
    talla = models.CharField(max_length=10, choices=TALLA_CHOICES, default='UNICA')

    precio = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)

    # HU-30: marcar agotado o eliminar
    agotado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)  # "eliminar" lógico, no físico

    # HU-31: ofertas y descuentos
    en_oferta = models.BooleanField(default=False)
    porcentaje_descuento = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(90)],
        help_text="Porcentaje de descuento (0-90)"
    )

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-creado']

    def __str__(self):
        return f"{self.nombre} ({self.talla})"

    @property
    def precio_final(self):
        from decimal import Decimal
        if self.en_oferta and self.porcentaje_descuento > 0:
            descuento = self.precio * (Decimal(self.porcentaje_descuento) / Decimal(100))
            return round(self.precio - descuento, 2)
        return self.precio
    
    @property
    def imagen_portada(self):
        return self.imagenes.filter(es_portada=True).first() or self.imagenes.first()

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.subcategoria_id and self.categoria_id and self.subcategoria.categoria_id != self.categoria_id:
            raise ValidationError({
                'subcategoria': 'La subcategoría no pertenece a la categoría seleccionada.'
            })

    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.agotado = True
        self.full_clean()
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
            # Solo puede haber una portada por producto: desmarca las demás
            ImagenProducto.objects.filter(
                producto=self.producto, es_portada=True
            ).exclude(pk=self.pk).update(es_portada=False)
        super().save(*args, **kwargs)


class ConfiguracionNegocio(models.Model):
    """HU-37 y HU-40 — configuración general (singleton: una sola fila)"""

    # HU-40: datos bancarios y WhatsApp
    nombre_negocio = models.CharField(max_length=100, default="Mi Tienda")
    whatsapp_numero = models.CharField(max_length=20, help_text="Con código de país, ej: 59171234567")
    banco_nombre = models.CharField(max_length=100, blank=True)
    banco_titular = models.CharField(max_length=100, blank=True)
    banco_numero_cuenta = models.CharField(max_length=50, blank=True)
    qr_pago = models.ImageField(upload_to='configuracion/', blank=True, null=True)

    # HU-37: monto mínimo de apartado
    monto_minimo_apartado = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        validators=[MinValueValidator(0)]
    )

    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración del negocio"
        verbose_name_plural = "Configuración del negocio"

    def __str__(self):
        return self.nombre_negocio

    def save(self, *args, **kwargs):
        # Forzar que solo exista una fila (singleton)
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def obtener(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj