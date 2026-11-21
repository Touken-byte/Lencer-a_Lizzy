from datetime import datetime

from django.contrib.admin import site
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.db.models import Count, Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from pedidos.models import Pago, Pedido

MESES = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]


def salir_admin(request):
    if request.method == 'POST':
        logout(request)
        return redirect('admin:login')
    return render(request, 'admin/confirmar_salir.html')


def _clave(anio, mes):
    return f"{anio:04d}-{mes:02d}"


def _mes_solicitado(request, hoy):
    """Lee ?mes=AAAA-MM; si no es válido, usa el mes actual."""
    try:
        anio, mes = request.GET.get('mes', '').split('-')
        anio, mes = int(anio), int(mes)
        if 1 <= mes <= 12 and 2000 <= anio <= 2100:
            return anio, mes
    except ValueError:
        pass
    return hoy.year, hoy.month


def _desglose(qs, campo, choices):
    nombres = dict(choices)
    filas = qs.values(campo).annotate(n=Count('id'), total=Sum('total')).order_by(campo)
    return [
        {'nombre': nombres.get(f[campo], f[campo]), 'n': f['n'], 'total': f['total'] or 0}
        for f in filas
    ]


@staff_member_required
def resumen_ventas_admin(request):
    hoy = timezone.localtime(timezone.now())
    anio, mes = _mes_solicitado(request, hoy)

    inicio = timezone.make_aware(datetime(anio, mes, 1))
    if mes == 12:
        fin = timezone.make_aware(datetime(anio + 1, 1, 1))
        sig_anio, sig_mes = anio + 1, 1
    else:
        fin = timezone.make_aware(datetime(anio, mes + 1, 1))
        sig_anio, sig_mes = anio, mes + 1
    ant_anio, ant_mes = (anio - 1, 12) if mes == 1 else (anio, mes - 1)

    pedidos_mes = Pedido.objects.filter(
        fecha_venta__gte=inicio, fecha_venta__lt=fin
    ).exclude(estado='cancelado')

    pagos = Pago.objects.filter(pedido__in=pedidos_mes)
    nombres_metodo = dict(Pago.METODO_CHOICES)
    por_metodo = [
        {'nombre': nombres_metodo.get(f['metodo'], f['metodo']), 'n': f['cantidad']}
        for f in pagos.values('metodo').annotate(cantidad=Count('id')).order_by('-cantidad')
    ]

    es_mes_actual = (anio, mes) == (hoy.year, hoy.month)
    context = {
        **site.each_context(request),
        'title': 'Resumen de ventas',
        'titulo_mes': f"{MESES[mes - 1]} {anio}",
        'mes_clave': _clave(anio, mes),
        'mes_anterior': _clave(ant_anio, ant_mes),
        'mes_siguiente': None if es_mes_actual or (anio, mes) > (hoy.year, hoy.month) else _clave(sig_anio, sig_mes),
        'mes_hoy': _clave(hoy.year, hoy.month),
        'total_pedidos': pedidos_mes.count(),
        'monto_total': pedidos_mes.aggregate(total=Sum('total'))['total'] or 0,
        'entregados': pedidos_mes.filter(estado='entregado').count(),
        'por_metodo': por_metodo,
        'por_lugar': _desglose(pedidos_mes, 'lugar_venta', Pedido.LUGAR_VENTA_CHOICES),
        'por_origen': _desglose(pedidos_mes, 'origen', Pedido.ORIGEN_CHOICES),
    }
    return render(request, 'admin/frontend/resumen_ventas.html', context)
