"""
Exporta el dataset de ventas DIRECTO desde la base de datos: una fila por línea de pedido.
El notebook de ciencia de datos parte de este CSV.

Por defecto excluye los pedidos de prueba (origen='prueba'). Los pedidos con origen='estimado'
son ventas reconstruidas; la columna 'origen' viaja en el dataset para poder identificarlas.

Uso:
    python manage.py exportar_dataset_ventas
    python manage.py exportar_dataset_ventas --salida datos/ventas_lineas.csv --incluir-pruebas
"""
import csv

from django.core.management.base import BaseCommand
from django.utils import timezone

from pedidos.models import ItemPedido

DIAS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']

COLUMNAS = [
    'pedido_id', 'fecha', 'dia_semana', 'mes', 'semana_iso', 'hora', 'lugar_venta', 'origen',
    'producto_id', 'producto', 'categoria', 'subcategoria', 'temporada',
    'talla', 'color', 'cantidad', 'precio_unitario', 'subtotal', 'metodo_pago',
]


class Command(BaseCommand):
    help = "Exporta las ventas (líneas de pedido) a un CSV para el análisis y el modelo"

    def add_arguments(self, parser):
        parser.add_argument('--salida', default='datos/ventas_lineas.csv')
        parser.add_argument('--incluir-pruebas', action='store_true',
                            help="Incluye también los pedidos con origen='prueba'")

    def handle(self, *args, **opts):
        qs = (ItemPedido.objects
              .select_related('pedido', 'pedido__pago', 'producto', 'producto__categoria',
                              'producto__subcategoria')
              .exclude(pedido__estado='cancelado')
              .order_by('pedido__fecha_venta', 'pedido_id', 'id'))
        if not opts['incluir_pruebas']:
            qs = qs.exclude(pedido__origen='prueba')

        filas = 0
        with open(opts['salida'], 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(COLUMNAS)
            for it in qs:
                p = it.pedido
                dt = timezone.localtime(p.fecha_venta) if timezone.is_aware(p.fecha_venta) else p.fecha_venta
                pago = getattr(p, 'pago', None)
                w.writerow([
                    p.id, dt.date().isoformat(), DIAS[dt.weekday()], dt.month, dt.isocalendar()[1], dt.hour,
                    p.lugar_venta, p.origen, it.producto_id, it.producto.nombre, it.producto.categoria.nombre,
                    it.producto.subcategoria.nombre, it.producto.temporada, it.talla, it.color, it.cantidad,
                    it.precio_unitario, it.cantidad * it.precio_unitario, pago.metodo if pago else '',
                ])
                filas += 1
        self.stdout.write(self.style.SUCCESS(f"{filas} filas exportadas a {opts['salida']}"))
