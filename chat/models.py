from django.db import models
from django.contrib.auth.models import User


class Mensaje(models.Model):
    """HU-16, HU-18, HU-19: chat entre clienta y vendedora"""

    EMISOR_CHOICES = [
        ('clienta', 'Clienta'),
        ('vendedora', 'Vendedora'),
    ]

    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='mensajes_chat',
        help_text="La clienta dueña de esta conversación"
    )
    emisor = models.CharField(max_length=10, choices=EMISOR_CHOICES)
    texto = models.CharField(max_length=1000, blank=True)
    imagen = models.ImageField(upload_to='chat/%Y/%m/', blank=True, null=True)
    video = models.FileField(upload_to='chat/videos/%Y/%m/', blank=True, null=True)
    automatico = models.BooleanField(default=False, help_text="Mensaje generado por el sistema (HU-19)")
    leido = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ['creado']

    def __str__(self):
        return f"{self.get_emisor_display()} -> {self.usuario.username}: {self.texto[:30]}"
    
class ImagenMensaje(models.Model):
    """Imágenes adicionales cuando se suben varias en un solo envío"""
    mensaje = models.ForeignKey(Mensaje, on_delete=models.CASCADE, related_name='imagenes_extra')
    imagen = models.ImageField(upload_to='chat/%Y/%m/')
    video = models.FileField(upload_to='chat/videos/%Y/%m/', blank=True, null=True)

    def __str__(self):
        return f"Imagen extra de mensaje #{self.mensaje_id}"