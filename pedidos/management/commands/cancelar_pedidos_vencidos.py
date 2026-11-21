from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from catalogo.models import VarianteProducto
from pedidos.models import Pedido


class Command(BaseCommand):
    help = ("Cancela pedidos online en efectivo sin pagar tras N dias y devuelve el stock. "
            "Solo toca origen='real' y lugar_venta='online'.")

    def add_arguments(self, parser):
        parser.add_argument('--dias', type=int, default=2)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **opts):
        limite = timezone.now() - timedelta(days=opts['dias'])
        vencidos = Pedido.objects.filter(
            origen='real', lugar_venta='online', estado='en_verificacion',
            creado__lt=limite, pago__metodo='efectivo', pago__estado='pendiente',
        ).prefetch_related('items')

        cancelados = 0
        for pedido in vencidos:
            if opts['dry_run']:
                self.stdout.write(f"[simulacion] pedido #{pedido.pk} se cancelaria")
                cancelados += 1
                continue
            with transaction.atomic():
                for item in pedido.items.all():
                    variante = VarianteProducto.objects.select_for_update().filter(
                        producto_id=item.producto_id, talla=item.talla, color__iexact=item.color
                    ).first()
                    if variante:
                        VarianteProducto.objects.filter(pk=variante.pk).update(
                            stock=F('stock') + item.cantidad
                        )
                    else:
                        self.stderr.write(f"pedido #{pedido.pk}: variante no encontrada, stock no devuelto")
                pedido.estado = 'cancelado'
                pedido.save(update_fields=['estado'])
            cancelados += 1
            self.stdout.write(f"pedido #{pedido.pk} cancelado y stock devuelto")
        self.stdout.write(f"Total: {cancelados}" + (" (DRY-RUN, no se guardo nada)" if opts['dry_run'] else ""))
