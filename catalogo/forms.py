from django import forms
from django.core.exceptions import ValidationError
from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'categoria', 'subcategoria', 'precio', 'activo', 'en_oferta', 'porcentaje_descuento']

    def clean(self):
        cleaned_data = super().clean()
        en_oferta = cleaned_data.get('en_oferta')
        porcentaje = cleaned_data.get('porcentaje_descuento')
        precio = cleaned_data.get('precio')
        subcategoria = cleaned_data.get('subcategoria')
        categoria = cleaned_data.get('categoria')

        if en_oferta and (not porcentaje or porcentaje <= 0):
            raise ValidationError({
                'porcentaje_descuento': 'Si el producto está en oferta, el descuento debe ser mayor a 0%.'
            })

        if not en_oferta and porcentaje and porcentaje > 0:
            raise ValidationError({
                'porcentaje_descuento': 'No se puede asignar un descuento si el producto no está marcado en oferta.'
            })

        if precio is not None and precio <= 0:
            raise ValidationError({'precio': 'El precio debe ser mayor a 0.'})

        if subcategoria and categoria and subcategoria.categoria_id != categoria.id:
            raise ValidationError({
                'subcategoria': 'La subcategoría seleccionada no pertenece a la categoría elegida.'
            })

        return cleaned_data