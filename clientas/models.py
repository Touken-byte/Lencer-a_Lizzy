from django.db import models
from django.contrib.auth.models import User
from catalogo.models import Producto


class PerfilCliente(models.Model):
    """HU-24: perfil con nombre, contacto y tallas"""

    TALLA_BRASSIERE_CHOICES = [
        ('70A', '70A'), ('70B', '70B'), ('70C', '70C'),
        ('75A', '75A'), ('75B', '75B'), ('75C', '75C'),
        ('80A', '80A'), ('80B', '80B'), ('80C', '80C'),
        ('85A', '85A'), ('85B', '85B'), ('85C', '85C'),
    ]
    TALLA_CALZON_CHOICES = [
        ('XS', 'XS'), ('S', 'S'), ('M', 'M'),
        ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_cliente')
    telefono = models.CharField(max_length=20, blank=True)
    talla_brassiere = models.CharField(max_length=5, choices=TALLA_BRASSIERE_CHOICES, blank=True)
    talla_calzon = models.CharField(max_length=5, choices=TALLA_CALZON_CHOICES, blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de clienta"
        verbose_name_plural = "Perfiles de clientas"

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class Favorito(models.Model):
    """HU-25: guardar productos en lista de deseos"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='favoritos_de')
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"
        unique_together = ('usuario', 'producto')
        ordering = ['-creado']

    def __str__(self):
        return f"{self.usuario.username} ❤ {self.producto.nombre}"