from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render, redirect

def salir_admin(request):
    logout(request)
    return redirect('admin:login')

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin import site
from django.db.models import Sum, Count
from django.utils import timezone
from pedidos.models import Pedido, Pago


@staff_member_required
def resumen_ventas_admin(request):
    hoy = timezone.now()
    pedidos_mes = Pedido.objects.filter(
        creado__year=hoy.year, creado__month=hoy.month
    ).exclude(estado='cancelado')

    total_pedidos = pedidos_mes.count()
    monto_total = pedidos_mes.aggregate(total=Sum('total'))['total'] or 0
    entregados = pedidos_mes.filter(estado='entregado').count()

    por_metodo = (
        Pago.objects.filter(pedido__in=pedidos_mes)
        .values('metodo')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')
    )

    context = {
        **site.each_context(request),
        'title': 'Resumen de ventas',
        'total_pedidos': total_pedidos,
        'monto_total': monto_total,
        'entregados': entregados,
        'por_metodo': por_metodo,
        'mes_actual': hoy.strftime('%B %Y'),
    }
    return render(request, 'admin/frontend/resumen_ventas.html', context)
