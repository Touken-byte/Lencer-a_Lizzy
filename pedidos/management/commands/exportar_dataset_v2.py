"""
Exporta la VERSIÓN 2 de los datos para el análisis: cuatro archivos en datos/v2/.
No reemplaza a exportar_dataset_ventas (versión 1): los notebooks v1 siguen funcionando.

  ventas_lineas.csv           una fila por línea de pedido (19 columnas de la v1 + 6 nuevas al final)
  pedidos.csv                 una fila por pedido
  catalogo_productos.csv      una fila por producto del catálogo
  metadatos_exportacion.json  conteos y totales, para que el notebook verifique lo que lee

Excluye pedidos cancelados y, por defecto, los de origen='prueba'.
No exporta datos de clientas (ni id, ni nombre, ni correo).

Uso:
    python manage.py exportar_dataset_v2
    python manage.py exportar_dataset_v2 --carpeta datos/v2 --incluir-pruebas
"""
import csv
import json
import os
from collections import Counter

from django.core.management.base import BaseCommand
from django.utils import timezone

from catalogo.models import Producto
from pedidos.models import Pedido

DIAS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']

COLS_LINEAS = [
    'pedido_id', 'fecha', 'dia_semana', 'mes', 'semana_iso', 'hora', 'lugar_venta', 'origen',
    'producto_id', 'producto', 'categoria', 'subcategoria', 'temporada',
    'talla', 'color', 'cantidad', 'precio_unitario', 'subtotal', 'metodo_pago',
    # nuevas en la versión 2
    'estado_pedido', 'estado_pago', 'tipo_entrega',
    'precio_lista_actual', 'en_oferta_actual', 'descuento_actual_pct',
]
COLS_PEDIDOS = [
    'pedido_id', 'fecha', 'dia_semana', 'hora', 'lugar_venta', 'origen', 'tipo_entrega',
    'estado_pedido', 'metodo_pago', 'estado_pago', 'n_lineas', 'n_prendas', 'total_pedido',
]
COLS_CATALOGO = [
    'producto_id', 'producto', 'categoria', 'subcategoria', 'temporada', 'precio',
    'en_oferta', 'descuento_pct', 'activo', 'n_variantes', 'stock_total',
]


def _local(dt):
    return timezone.localtime(dt) if timezone.is_aware(dt) else dt


class Command(BaseCommand):
    help = "Exporta la versión 2 del dataset de ventas (líneas, pedidos, catálogo y metadatos)"

    def add_arguments(self, parser):
        parser.add_argument('--carpeta', default='datos/v2')
        parser.add_argument('--incluir-pruebas', action='store_true',
                            help="Incluye también los pedidos con origen='prueba'")

    def handle(self, *args, **opts):
        carpeta = opts['carpeta']

        # Se leen TODOS los datos antes de escribir: si MySQL está apagado, falla sin dejar archivos vacíos.
        pedidos = (Pedido.objects.select_related('pago')
                   .prefetch_related('items__producto__categoria', 'items__producto__subcategoria')
                   .exclude(estado='cancelado').order_by('fecha_venta', 'id'))
        if not opts['incluir_pruebas']:
            pedidos = pedidos.exclude(origen='prueba')
        pedidos = [p for p in pedidos if p.items.all()]
        productos = list(Producto.objects.select_related('categoria', 'subcategoria')
                         .prefetch_related('variantes').order_by('id'))

        filas_lineas, filas_pedidos = [], []
        subtotal = 0
        prendas = 0
        total_pedidos = 0
        fechas = set()
        for p in pedidos:
            dt = _local(p.fecha_venta)
            pago = getattr(p, 'pago', None)
            metodo = pago.metodo if pago else ''
            estado_pago = pago.estado if pago else ''
            items = sorted(p.items.all(), key=lambda i: i.id)
            prendas_pedido = 0
            for it in items:
                pr = it.producto
                sub = it.cantidad * it.precio_unitario
                subtotal += sub
                prendas_pedido += it.cantidad
                filas_lineas.append([
                    p.id, dt.date().isoformat(), DIAS[dt.weekday()], dt.month, dt.isocalendar()[1], dt.hour,
                    p.lugar_venta, p.origen, it.producto_id, pr.nombre, pr.categoria.nombre,
                    pr.subcategoria.nombre, pr.temporada, it.talla, it.color, it.cantidad,
                    it.precio_unitario, sub, metodo,
                    p.estado, estado_pago, p.tipo_entrega,
                    pr.precio, int(pr.en_oferta), pr.porcentaje_descuento,
                ])
            prendas += prendas_pedido
            total_pedidos += p.total
            fechas.add(dt.date().isoformat())
            filas_pedidos.append([
                p.id, dt.date().isoformat(), DIAS[dt.weekday()], dt.hour, p.lugar_venta, p.origen,
                p.tipo_entrega, p.estado, metodo, estado_pago, len(items), prendas_pedido, p.total,
            ])

        filas_catalogo = []
        for pr in productos:
            variantes = list(pr.variantes.all())
            filas_catalogo.append([
                pr.id, pr.nombre, pr.categoria.nombre, pr.subcategoria.nombre, pr.temporada, pr.precio,
                int(pr.en_oferta), pr.porcentaje_descuento, int(pr.activo),
                len(variantes), sum(v.stock for v in variantes),
            ])

        os.makedirs(carpeta, exist_ok=True)
        for nombre, cols, filas in [('ventas_lineas.csv', COLS_LINEAS, filas_lineas),
                                    ('pedidos.csv', COLS_PEDIDOS, filas_pedidos),
                                    ('catalogo_productos.csv', COLS_CATALOGO, filas_catalogo)]:
            with open(os.path.join(carpeta, nombre), 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(cols)
                w.writerows(filas)

        meta = {
            'version': 2,
            'fecha_exportacion': timezone.now().isoformat(timespec='seconds'),
            'incluye_pruebas': bool(opts['incluir_pruebas']),
            'lineas': len(filas_lineas),
            'pedidos': len(filas_pedidos),
            'prendas': int(prendas),
            'subtotal_lineas_bs': float(round(subtotal, 2)),
            'total_pedidos_bs': float(round(total_pedidos, 2)),
            'dias_distintos': len(fechas),
            'fecha_min': min(fechas) if fechas else None,
            'fecha_max': max(fechas) if fechas else None,
            'pedidos_por_origen': dict(Counter(f[5] for f in filas_pedidos)),
            'pedidos_por_lugar': dict(Counter(f[4] for f in filas_pedidos)),
            'productos_catalogo': len(filas_catalogo),
            'columnas_lineas': COLS_LINEAS,
        }
        with open(os.path.join(carpeta, 'metadatos_exportacion.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f"v2 exportada en {carpeta}/: {len(filas_lineas)} líneas, {len(filas_pedidos)} pedidos, "
            f"{len(filas_catalogo)} productos, subtotal Bs {meta['subtotal_lineas_bs']:.2f}"))
