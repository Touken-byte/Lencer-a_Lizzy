from django import forms
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from clientas.models import PerfilCliente


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo")
    telefono = forms.CharField(max_length=20, required=False, label="Teléfono")
    genero = forms.ChoiceField(
        choices=PerfilCliente.GENERO_CHOICES, required=False, label="Género",
        widget=forms.Select(attrs={'id': 'id_genero'})
    )
    talla_calzon = forms.ChoiceField(
        choices=[('', '---------')] + PerfilCliente.TALLA_CALZON_CHOICES,
        required=False, label="Talla de calzón"
    )
    talla_brassiere = forms.ChoiceField(
        choices=[('', '---------')] + PerfilCliente.TALLA_BRASSIERE_CHOICES,
        required=False, label="Talla de brasier"
    )

    acepta_terminos = forms.BooleanField(
        required=True,
        error_messages={'required': 'Debes aceptar los Términos y la Política de Privacidad para registrarte.'},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'acepta_terminos':
                field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean(self):
        datos = super().clean()
        if datos.get('genero') != 'mujer':
            datos['talla_brassiere'] = ''
        return datos

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            PerfilCliente.objects.create(
                usuario=user,
                telefono=self.cleaned_data.get('telefono', ''),
                genero=self.cleaned_data.get('genero', ''),
                talla_calzon=self.cleaned_data.get('talla_calzon', ''),
                talla_brassiere=self.cleaned_data.get('talla_brassiere', ''),
                consentimiento_fecha=timezone.now(),
            )
        return user


class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False, label="Nombre")
    email = forms.EmailField(required=False, label="Correo")

    class Meta:
        model = PerfilCliente
        fields = ['genero', 'telefono', 'talla_brassiere', 'talla_calzon']
        labels = {
            'genero': 'Género', 'telefono': 'Teléfono',
            'talla_brassiere': 'Talla de brasier', 'talla_calzon': 'Talla de calzón',
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if self.usuario:
            self.fields['first_name'].initial = self.usuario.first_name
            self.fields['email'].initial = self.usuario.email
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        if self.usuario and self.usuario.username == settings.DEMO_USUARIO:
            # Cuenta demo protegida: no se puede cambiar el correo de acceso
            self.fields['email'].disabled = True

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email:
            otros = User.objects.filter(email__iexact=email)
            if self.usuario:
                otros = otros.exclude(pk=self.usuario.pk)
            if otros.exists():
                raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean(self):
        datos = super().clean()
        if datos.get('genero') != 'mujer':
            datos['talla_brassiere'] = ''
        return datos

    def save(self, commit=True):
        perfil = super().save(commit=False)
        if self.usuario:
            self.usuario.first_name = self.cleaned_data.get('first_name', '')
            self.usuario.email = self.cleaned_data.get('email', '')
            if commit:
                self.usuario.save()
        if commit:
            perfil.save()
        return perfil
