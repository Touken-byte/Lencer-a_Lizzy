"""
Importa ventas ESTIMADAS (reconstruidas) desde un archivo de texto.

Cada venta queda como pedido ENTREGADO con pago VERIFICADO (venta presencial ya cobrada),
con origen='estimado' y fecha_venta = fecha/hora estimada de la venta. No toca el stock ni 'creado'.
Es idempotente: si una referencia (VE-xxxx) ya existe, la omite.

Formato del archivo:
    ### LUNES 03/08/2026 | LOURDES | 6 pedidos | Bs 184.30      (LOURDES o BARRIO NUEVO)
    VE-0001 11:58 | Calzón faja L verde + Bikini M azul Bs36.00 | QR
  Cada ítem: Producto TALLA color [xN] [BsPRECIO]. El precio Bs es obligatorio si el nombre está repetido.

Uso:
    python manage.py importar_ventas_estimadas datos/ventas_estimadas.txt \
        --usuario-lourdes NOMBRE --usuario-barrio NOMBRE --dry-run
"""
import re
import unicodedata
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalogo.models import Producto
from pedidos.models import Pedido, ItemPedido, Pago

CAB = re.compile(r'^###\s+\S+\s+(\d{2})/(\d{2})/(\d{4})\s*\|\s*(.+)$')
PED = re.compile(r'^(VE-\d+)\s+(\d{1,2}):(\d{2})\s*\|\s*(.+?)(?:\s*\|\s*(QR))?\s*$')
ITEM = re.compile(r'^(?P<n>.+?)\s+(?P<t>\S+)\s+(?P<c>\S+?)(?:\s+x(?P<q>\d+))?(?:\s+Bs(?P<bs>\d+(?:\.\d+)?))?$')


def norm(s):
    s = unicodedata.normalize('NFD', s.strip().lower())
    return ' '.join(''.join(c for c in s if unicodedata.category(c) != 'Mn').split())


class Command(BaseCommand):
    help = "Importa ventas estimadas desde un archivo de texto (entregadas y con pago verificado)"

    def add_arguments(self, parser):
        parser.add_argument('archivo')
        parser.add_argument('--usuario-lourdes', required=True)
        parser.add_argument('--usuario-barrio', required=True)
        parser.add_argument('--dry-run', action='store_true', help='Valida y simula; no guarda nada')

    def _resolver(self, catalogo, nombre, bs):
        n = norm(nombre)
        cands = catalogo.get(n)
        if not cands and n in ('ropa usada mujer', 'ropa usada hombre'):
            cat = 'mujer' if n.endswith('mujer') else 'hombre'
            cands = [p for p in catalogo.get('ropa usada', []) if norm(p.categoria.nombre) == cat]
        if not cands:
            raise ValueError(f"producto no encontrado: '{nombre}'")
        if bs is not None:
            ok = [p for p in cands if abs(p.precio_final - bs) < Decimal('0.005')]
            if not ok:
                precios = ', '.join(sorted({str(p.precio_final) for p in cands}))
                raise ValueError(f"'{nombre}': ningún producto cuesta Bs{bs} (precios existentes: {precios})")
            return ok[0], bs
        if len(cands) > 1:
            raise ValueError(f"'{nombre}': hay {len(cands)} productos con ese nombre; falta el precio Bs")
        return cands[0], cands[0].precio_final

    def _leer(self, ruta, catalogo):
        dias, errores, dia = [], [], None
        try:
            with open(ruta, encoding='utf-8') as f:
                lineas = f.read().splitlines()
        except OSError as e:
            raise CommandError(f"No pude abrir {ruta}: {e}")
        for i, linea in enumerate(lineas, 1):
            linea = linea.strip()
            if not linea:
                continue
            m = CAB.match(linea)
            if m:
                d, mo, y, resto = m.groups()
                low = resto.lower()
                if 'lourdes' in low:
                    lugar = 'mercado_lourdes'
                elif 'barrio' in low:
                    lugar = 'feria_barrio_nuevo'
                else:
                    errores.append(f"línea {i}: cabecera sin LOURDES ni BARRIO: {linea}")
                    continue
                n = re.search(r'(\d+)\s+pedidos', resto)
                t = re.search(r'Bs\s*([\d.]+)', resto)
                dia = dict(fecha=(int(y), int(mo), int(d)), lugar=lugar,
                           esp_n=int(n.group(1)) if n else None,
                           esp_t=Decimal(t.group(1)) if t else None, pedidos=[])
                dias.append(dia)
                continue
            m = PED.match(linea)
            if not m or dia is None:
                errores.append(f"línea {i}: no entiendo: {linea}")
                continue
            ref, hh, mm, cuerpo, qr = m.groups()
            items, ok = [], True
            for trozo in cuerpo.split(' + '):
                mi = ITEM.match(trozo.strip())
                if not mi:
                    errores.append(f"línea {i} ({ref}): ítem ilegible: '{trozo}'")
                    ok = False
                    continue
                bs = Decimal(mi.group('bs')) if mi.group('bs') else None
                try:
                    prod, precio = self._resolver(catalogo, mi.group('n'), bs)
                except ValueError as e:
                    errores.append(f"línea {i} ({ref}): {e}")
                    ok = False
                    continue
                items.append(dict(prod=prod, precio=precio, talla=mi.group('t'), color=mi.group('c'),
                                  q=int(mi.group('q') or 1)))
            if ok:
                dia['pedidos'].append(dict(ref=ref, hh=int(hh), mm=int(mm), items=items, qr=bool(qr)))
        return dias, errores

    @transaction.atomic
    def handle(self, *args, **o):
        User = get_user_model()
        try:
            usuarios = {'mercado_lourdes': User.objects.get(username=o['usuario_lourdes']),
                        'feria_barrio_nuevo': User.objects.get(username=o['usuario_barrio'])}
        except User.DoesNotExist as e:
            raise CommandError(f"No existe uno de los usuarios indicados: {e}")

        catalogo = defaultdict(list)
        for p in Producto.objects.select_related('categoria'):
            catalogo[norm(p.nombre)].append(p)

        dias, errores = self._leer(o['archivo'], catalogo)
        if errores:
            for e in errores[:60]:
                self.stdout.write(self.style.ERROR(e))
            raise CommandError(f"{len(errores)} problema(s) en el archivo. No se guardó nada.")

        creados = omitidos = diferencias = 0
        for dia in dias:
            y, mo, d = dia['fecha']
            n_dia, t_dia = 0, Decimal('0')
            for ped in dia['pedidos']:
                existente = Pedido.objects.filter(nota=ped['ref']).first()
                if existente:
                    omitidos += 1
                    n_dia += 1
                    t_dia += existente.total
                    continue
                dt = datetime(y, mo, d, ped['hh'], ped['mm'])
                if settings.USE_TZ:
                    dt = timezone.make_aware(dt)
                pedido = Pedido.objects.create(
                    clienta=usuarios[dia['lugar']], direccion=None, tipo_entrega='tienda', nota=ped['ref'],
                    estado='entregado', total=Decimal('0'), fecha_venta=dt, lugar_venta=dia['lugar'],
                    origen='estimado')
                for it in ped['items']:
                    ItemPedido.objects.create(pedido=pedido, producto=it['prod'], talla=it['talla'],
                                              color=it['color'], cantidad=it['q'], precio_unitario=it['precio'])
                pedido.recalcular_total()
                Pago.objects.create(pedido=pedido, metodo='qr' if ped['qr'] else 'efectivo',
                                    estado='verificado', nombre_referencia='')
                creados += 1
                n_dia += 1
                t_dia += pedido.total
            estado = 'OK'
            if dia['esp_n'] is not None and (n_dia != dia['esp_n'] or t_dia != dia['esp_t']):
                estado = f"DIFERENCIA (esperado {dia['esp_n']} / Bs {dia['esp_t']})"
                diferencias += 1
            linea = f"{y}-{mo:02d}-{d:02d} {dia['lugar']:<19} {n_dia:>3} pedidos  Bs {t_dia:>8}  {estado}"
            self.stdout.write(self.style.SUCCESS(linea) if estado == 'OK' else self.style.WARNING(linea))

        self.stdout.write(f"\nCreados: {creados} | omitidos (ya existían): {omitidos} | días con diferencia: {diferencias}")
        if o['dry_run']:
            transaction.set_rollback(True)
            self.stdout.write(self.style.WARNING("DRY-RUN: no se guardó nada."))
