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
        ('domicilio', 'Envío a domicilio'),
        ('recogida', 'Recogida en punto físico'),
    ]
    tipo_entrega = forms.ChoiceField(choices=TIPO_ENTREGA_CHOICES, widget=forms.RadioSelect)
    direccion = forms.ModelChoiceField(
        queryset=DireccionEntrega.objects.none(), required=False, label="Dirección de entrega"
    )
    nota = forms.CharField(
        max_length=300, required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )
    metodo_pago = forms.ChoiceField(choices=Pago.METODO_CHOICES, widget=forms.RadioSelect)

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['direccion'].queryset = DireccionEntrega.objects.filter(usuario=usuario)
