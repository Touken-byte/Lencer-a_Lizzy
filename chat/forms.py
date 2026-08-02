from django import forms
from .models import Mensaje

MAX_IMAGEN_MB = 5
MAX_VIDEO_MB = 20
MAX_VIDEO_SEGUNDOS = 60


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
        return imagenes

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            if video.size > MAX_VIDEO_MB * 1024 * 1024:
                raise forms.ValidationError(f"El video debe pesar como máximo {MAX_VIDEO_MB} MB.")
            if not video.content_type.startswith('video/'):
                raise forms.ValidationError("El archivo debe ser un video.")
        return video

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('texto') and not self.files.getlist('imagenes') and not cleaned.get('video'):
            raise forms.ValidationError("Escribe un mensaje o adjunta una imagen/video.")
        return cleaned