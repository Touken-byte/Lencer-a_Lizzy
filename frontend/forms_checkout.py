from django import forms
from clientas.models import DireccionEntrega
from pedidos.models import Pago


class DireccionForm(forms.ModelForm):
    class Meta:
        model = DireccionEntrega
        fields = ['nombre_referencia', 'calle', 'barrio', 'referencias', 'es_predeterminada']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'es_predeterminada':
                field.widget.attrs.update({'class': 'form-control'})


class CheckoutForm(forms.Form):
    TIPO_ENTREGA_CHOICES = [
        ('recogida', 'Recogida en punto físico'),
        ('tienda', 'Recogida en tienda física'),
    ]
    tipo_entrega = forms.ChoiceField(
        choices=TIPO_ENTREGA_CHOICES, widget=forms.RadioSelect, initial='recogida'
    )
    nota = forms.CharField(
        max_length=300, required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ej: llamar antes de llegar'})
    )
    metodo_pago = forms.ChoiceField(choices=Pago.METODO_CHOICES, widget=forms.RadioSelect)
    nombre_referencia = forms.CharField(
        max_length=100, required=False,
        label="Nombre con el que pagarás (para identificar tu pago)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: María Pérez'})
    )

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
