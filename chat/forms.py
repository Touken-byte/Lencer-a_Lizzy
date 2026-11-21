import os

from django import forms
from PIL import Image
from .models import Mensaje

MAX_IMAGEN_MB = 5
MAX_VIDEO_MB = 20

EXT_IMAGEN = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
EXT_VIDEO = {'.mp4', '.webm', '.mov'}


def imagen_valida(archivo):
    """Extensión permitida y contenido realmente de imagen."""
    if os.path.splitext(archivo.name)[1].lower() not in EXT_IMAGEN:
        return False
    try:
        archivo.seek(0)
        Image.open(archivo).verify()
        return True
    except Exception:
        return False
    finally:
        archivo.seek(0)


def video_valido(archivo):
    """Firma real del contenedor (el content_type lo manda el cliente y se falsifica)."""
    ext = os.path.splitext(archivo.name)[1].lower()
    try:
        archivo.seek(0)
        cabecera = archivo.read(12)
    finally:
        archivo.seek(0)
    if ext == '.webm':
        return cabecera[:4] == b'\x1a\x45\xdf\xa3'
    if ext == '.mov':
        return cabecera[4:8] in (b'ftyp', b'moov', b'mdat', b'wide', b'free', b'skip')
    return cabecera[4:8] == b'ftyp'


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class MensajeForm(forms.ModelForm):
    imagenes = MultipleFileField(required=False, label="Imágenes")
    video = forms.FileField(required=False, label="Video")

    class Meta:
        model = Mensaje
        fields = ['texto', 'video']
        widgets = {
            'texto': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Escribe un mensaje...'
            }),
        }

    def clean_imagenes(self):
        imagenes = self.files.getlist('imagenes') if hasattr(self, 'files') else []
        for img in imagenes:
            if img.size > MAX_IMAGEN_MB * 1024 * 1024:
                raise forms.ValidationError(f"Cada imagen debe pesar como máximo {MAX_IMAGEN_MB} MB.")
            if not imagen_valida(img):
                raise forms.ValidationError("Solo se permiten imágenes JPG, PNG, WEBP o GIF.")
        return imagenes

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            if video.size > MAX_VIDEO_MB * 1024 * 1024:
                raise forms.ValidationError(f"El video debe pesar como máximo {MAX_VIDEO_MB} MB.")
            if not video.content_type.startswith('video/'):
                raise forms.ValidationError("El archivo debe ser un video.")
            if os.path.splitext(video.name)[1].lower() not in EXT_VIDEO:
                raise forms.ValidationError("Formato de video no permitido (MP4, WEBM o MOV).")
            if not video_valido(video):
                raise forms.ValidationError("El archivo no parece un video válido.")
        return video

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('texto') and not self.files.getlist('imagenes') and not cleaned.get('video'):
            raise forms.ValidationError("Escribe un mensaje o adjunta una imagen/video.")
        return cleaned