from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from clientas.models import PerfilCliente


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo")
    telefono = forms.CharField(max_length=20, required=False, label="Teléfono")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            PerfilCliente.objects.create(
                usuario=user,
                telefono=self.cleaned_data.get('telefono', '')
            )
        return user


class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False, label="Nombre")
    email = forms.EmailField(required=False, label="Correo")

    class Meta:
        model = PerfilCliente
        fields = ['telefono', 'talla_brassiere', 'talla_calzon']

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if self.usuario:
            self.fields['first_name'].initial = self.usuario.first_name
            self.fields['email'].initial = self.usuario.email
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

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
