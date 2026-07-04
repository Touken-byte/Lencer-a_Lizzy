from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import PerfilCliente, Favorito
from catalogo.serializers import ProductoListaSerializer


class RegistroClienteSerializer(serializers.ModelSerializer):
    """HU-24: registro con nombre, contacto y tallas. Registro con teléfono o correo."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    telefono = serializers.CharField(required=False, allow_blank=True)
    talla_brassiere = serializers.ChoiceField(
        choices=PerfilCliente.TALLA_BRASSIERE_CHOICES, required=False, allow_blank=True
    )
    talla_calzon = serializers.ChoiceField(
        choices=PerfilCliente.TALLA_CALZON_CHOICES, required=False, allow_blank=True
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email', 'password', 'telefono', 'talla_brassiere', 'talla_calzon']
        extra_kwargs = {'email': {'required': False}}

    def validate(self, data):
        # HU-24: registro con teléfono O correo (al menos uno de los dos)
        if not data.get('email') and not data.get('telefono'):
            raise serializers.ValidationError(
                "Debes proporcionar al menos un correo o un teléfono para registrarte."
            )
        return data

    def create(self, validated_data):
        telefono = validated_data.pop('telefono', '')
        talla_brassiere = validated_data.pop('talla_brassiere', '')
        talla_calzon = validated_data.pop('talla_calzon', '')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        PerfilCliente.objects.create(
            usuario=user,
            telefono=telefono,
            talla_brassiere=talla_brassiere,
            talla_calzon=talla_calzon,
        )
        return user


class PerfilClienteSerializer(serializers.ModelSerializer):
    """HU-24: datos editables del perfil"""
    nombre = serializers.CharField(source='usuario.first_name')
    email = serializers.EmailField(source='usuario.email', required=False)

    class Meta:
        model = PerfilCliente
        fields = ['nombre', 'email', 'telefono', 'talla_brassiere', 'talla_calzon']

    def update(self, instance, validated_data):
        usuario_data = validated_data.pop('usuario', {})
        if 'first_name' in usuario_data:
            instance.usuario.first_name = usuario_data['first_name']
        if 'email' in usuario_data:
            instance.usuario.email = usuario_data['email']
        instance.usuario.save()

        return super().update(instance, validated_data)


class FavoritoSerializer(serializers.ModelSerializer):
    """HU-25: lista de deseos"""
    producto_detalle = ProductoListaSerializer(source='producto', read_only=True)

    class Meta:
        model = Favorito
        fields = ['id', 'producto', 'producto_detalle', 'creado']
        read_only_fields = ['creado']

    def get_fields(self):
        fields = super().get_fields()
        fields['producto'].write_only = True
        return fields