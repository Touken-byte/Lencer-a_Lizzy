from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from catalogo.models import Producto
from clientas.models import PerfilCliente, DireccionEntrega, Favorito
from pedidos.models import Pedido, ItemPedido, Pago


class Command(BaseCommand):
    help = (
        "Crea (o reinicia con --reiniciar) la cuenta de demostración con datos ficticios. "
        "Usuario y contraseña salen de DEMO_USUARIO y DEMO_PASSWORD (.env)."
    )

    def add_arguments(self, parser):
        parser.add_argument('--reiniciar', action='store_true',
                            help="Borra los pedidos, favoritos y direcciones demo y los vuelve a crear.")

    @transaction.atomic
    def handle(self, *args, **opciones):
        nombre = settings.DEMO_USUARIO
        usuario, creado = User.objects.get_or_create(
            username=nombre,
            defaults={'email': 'demo@ejemplo.com', 'first_name': 'Cuenta Demo'},
        )
        usuario.is_staff = False
        usuario.is_superuser = False
        usuario.set_password(settings.DEMO_PASSWORD)
        usuario.save()

        PerfilCliente.objects.get_or_create(
            usuario=usuario,
            defaults={'telefono': '70000000', 'genero': 'mujer', 'talla_calzon': 'M',
                      'talla_brassiere': '75B', 'consentimiento_fecha': timezone.now()},
        )

        if opciones['reiniciar']:
            Pedido.objects.filter(clienta=usuario).delete()
            Favorito.objects.filter(usuario=usuario).delete()
            DireccionEntrega.objects.filter(usuario=usuario).delete()

        if not DireccionEntrega.objects.filter(usuario=usuario).exists():
            DireccionEntrega.objects.create(
                usuario=usuario, nombre_referencia='Casa (ficticia)', calle='Calle Ejemplo 123',
                barrio='Barrio Ficticio', referencias='Dirección de demostración', es_predeterminada=True)

        productos = list(Producto.objects.filter(activo=True).prefetch_related('variantes')[:6])
        for producto in productos[:3]:
            Favorito.objects.get_or_create(usuario=usuario, producto=producto)

        if not Pedido.objects.filter(clienta=usuario).exists() and productos:
            plan = [
                ('en_verificacion', 'qr', 0, 'pendiente'),
                ('confirmado', 'efectivo', 3, 'verificado'),
                ('entregado', 'qr', 12, 'verificado'),
                ('cancelado', 'efectivo', 20, 'pendiente'),
            ]
            for i, (estado, metodo, dias, estado_pago) in enumerate(plan):
                pedido = Pedido.objects.create(
                    clienta=usuario, tipo_entrega='tienda' if i % 2 else 'recogida',
                    origen='prueba', nota='Pedido de demostración',
                    fecha_venta=timezone.now() - timedelta(days=dias))
                for producto in productos[i:i + 2]:
                    variante = producto.variantes.first()
                    ItemPedido.objects.create(
                        pedido=pedido, producto=producto,
                        talla=variante.talla if variante else 'M',
                        color=variante.color if variante else '',
                        cantidad=1 + i % 2, precio_unitario=producto.precio_final)
                pedido.recalcular_total()
                Pago.objects.create(pedido=pedido, metodo=metodo, estado=estado_pago,
                                    nombre_referencia='Cliente Demo')
                if pedido.estado != estado:
                    Pedido.objects.filter(pk=pedido.pk).update(estado=estado)

        self.stdout.write(self.style.SUCCESS(
            f"Cuenta demo lista: usuario '{nombre}' ({'creada' if creado else 'actualizada'})."))
