from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalogo.models import Categoria, Producto, VarianteProducto, ConfiguracionNegocio
from django.db import transaction
from .carrito import Carrito
from .forms_checkout import DireccionForm, CheckoutForm
from pedidos.models import Pedido, ItemPedido, Pago
from catalogo.models import Categoria, Producto
from clientas.models import PerfilCliente, Favorito
from .forms import RegistroForm, PerfilForm
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test

def inicio(request):
    ofertas = (
        Producto.objects.filter(activo=True, en_oferta=True)
        .select_related('categoria')
        .prefetch_related('imagenes')[:8]
    )
    return render(request, 'frontend/inicio.html', {'ofertas': ofertas})


def catalogo(request):
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('q', '').strip()
    talla = request.GET.get('talla', '')
    color = request.GET.get('color', '')

    categorias = Categoria.objects.prefetch_related('subcategorias').all()
    productos = (
        Producto.objects.filter(activo=True)
        .select_related('categoria', 'subcategoria')
        .prefetch_related('imagenes')
    )

    mi_talla = request.GET.get('mi_talla')
    if mi_talla and request.user.is_authenticated:
        perfil_cliente = getattr(request.user, 'perfil_cliente', None)
        if perfil_cliente:
            from django.db.models import Q

            GENERO_A_CATEGORIAS = {
                'mujer': ['Mujer', 'Otros'],
                'hombre': ['Hombre', 'Otros'],
                'otro': None,  # "Otro" no restringe por categoría, ve de todo
            }

            filtro_talla = Q()
            if perfil_cliente.talla_calzon:
                filtro_talla |= Q(subcategoria__tipo_talla='letra', variantes__talla=perfil_cliente.talla_calzon)
            if perfil_cliente.talla_brassiere:
                filtro_talla |= Q(subcategoria__tipo_talla='brassiere', variantes__talla=perfil_cliente.talla_brassiere)

            if filtro_talla:
                productos = productos.filter(filtro_talla)

            categorias_genero = GENERO_A_CATEGORIAS.get(perfil_cliente.genero)
            if categorias_genero:
                productos = productos.filter(categoria__nombre__in=categorias_genero)

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    if talla:
        productos = productos.filter(variantes__talla=talla)
    if color:
        productos = productos.filter(variantes__color__iexact=color)

    productos = productos.distinct()

    colores_disponibles = (
        VarianteProducto.objects.filter(producto__activo=True)
        .exclude(color='')
        .values_list('color', flat=True)
        .distinct()
        .order_by('color')
    )

    favoritos_ids = set()
    if request.user.is_authenticated:
        favoritos_ids = set(
            Favorito.objects.filter(usuario=request.user).values_list('producto_id', flat=True)
        )

    context = {
        'categorias': categorias,
        'productos': productos,
        'categoria_activa': int(categoria_id) if categoria_id else None,
        'busqueda': busqueda,
        'talla_activa': talla,
        'color_activo': color,
        'tallas': Producto.TALLA_CHOICES,
        'colores_disponibles': colores_disponibles,
        'favoritos_ids': favoritos_ids,
    }
    return render(request, 'frontend/catalogo.html', context)


def producto_detalle(request, pk):
    producto = get_object_or_404(
        Producto.objects.prefetch_related('imagenes'), pk=pk, activo=True
    )
    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, producto=producto).exists()
    return render(request, 'frontend/producto_detalle.html', {
        'producto': producto,
        'es_favorito': es_favorito,
    })


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            genero = form.cleaned_data.get('genero') or 'otro'
            nombre = user.first_name or user.username
            return render(request, 'frontend/bienvenida.html', {'nombre': nombre, 'genero': genero})
    else:
        form = RegistroForm()
    return render(request, 'frontend/registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            ultimo_login = user.last_login
            auth_login(request, user)
            if ultimo_login:
                nuevos = Producto.objects.filter(activo=True, creado__gt=ultimo_login).count()
                if nuevos > 0:
                    messages.info(request, f"¡Hay {nuevos} producto(s) nuevo(s) desde tu última visita!")
            return redirect('frontend:catalogo')
    else:
        form = AuthenticationForm()
    form.fields['username'].widget.attrs.update({'class': 'form-control'})
    form.fields['password'].widget.attrs.update({'class': 'form-control'})
    return render(request, 'frontend/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        auth_logout(request)
    return redirect('frontend:inicio')


@login_required(login_url='frontend:login')
def perfil(request):
    perfil_cliente, _ = PerfilCliente.objects.get_or_create(usuario=request.user)
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil_cliente, usuario=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('frontend:perfil')
    else:
        form = PerfilForm(instance=perfil_cliente, usuario=request.user)
    return render(request, 'frontend/perfil.html', {'form': form})


@login_required(login_url='frontend:login')
def favoritos_lista(request):
    favoritos = (
        Favorito.objects.filter(usuario=request.user)
        .select_related('producto')
        .prefetch_related('producto__imagenes')
    )
    return render(request, 'frontend/favoritos.html', {'favoritos': favoritos})


@login_required(login_url='frontend:login')
def favorito_toggle(request, producto_id):
    if request.method == 'POST':
        favorito, creado = Favorito.objects.get_or_create(usuario=request.user, producto_id=producto_id)
        if not creado:
            favorito.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'es_favorito': creado})

    siguiente = request.POST.get('siguiente') or 'frontend:catalogo'
    return redirect(siguiente)

def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        talla = request.POST.get('talla', 'UNICA')
        color = request.POST.get('color', '')
        cantidad = int(request.POST.get('cantidad', 1))
        carrito = Carrito(request)
        carrito.agregar(producto_id, talla, color, cantidad)
        messages.success(request, "Producto agregado al carrito.")
    siguiente = request.POST.get('siguiente') or 'frontend:catalogo'
    return redirect(siguiente)

def ver_carrito(request):
    carrito = Carrito(request)
    return render(request, 'frontend/carrito.html', {
        'items': carrito.obtener_items(),
        'total': carrito.total(),
    })


def actualizar_carrito(request, clave):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        carrito = Carrito(request)
        carrito.actualizar_cantidad(clave, cantidad)
    return redirect('frontend:ver_carrito')


def eliminar_del_carrito(request, clave):
    if request.method == 'POST':
        carrito = Carrito(request)
        carrito.eliminar(clave)
    return redirect('frontend:ver_carrito')


@login_required(login_url='frontend:login')
def checkout(request):
    carrito = Carrito(request)
    items = carrito.obtener_items()

    if not items:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('frontend:catalogo')

    if request.method == 'POST':
        form = CheckoutForm(request.POST, usuario=request.user)
        if form.is_valid():
            with transaction.atomic():
                variantes_bloqueadas = {}
                for item in items:
                    variante = VarianteProducto.objects.select_for_update().filter(
                        producto=item['producto'], talla=item['talla'], color=item['color']
                    ).first()
                    if not variante or variante.stock < item['cantidad']:
                        disponibles = variante.stock if variante else 0
                        etiqueta = item['talla']
                        if item['color']:
                            etiqueta += f" - {item['color']}"
                        messages.error(
                            request,
                            f"No hay suficiente stock de {item['producto'].nombre} ({etiqueta}): "
                            f"pediste {item['cantidad']}, quedan {disponibles}."
                        )
                        return redirect('frontend:ver_carrito')
                    variantes_bloqueadas[item['clave']] = variante

                pedido = Pedido.objects.create(
                    clienta=request.user,
                    direccion=None,
                    tipo_entrega=form.cleaned_data['tipo_entrega'],
                    nota=form.cleaned_data['nota'],
                )
                for item in items:
                    variante = variantes_bloqueadas[item['clave']]
                    ItemPedido.objects.create(
                        pedido=pedido,
                        producto=item['producto'],
                        talla=item['talla'],
                        color=item['color'],
                        cantidad=item['cantidad'],
                        precio_unitario=item['producto'].precio_final,
                    )
                    variante.stock -= item['cantidad']
                    variante.save(update_fields=['stock'])

                pedido.recalcular_total()

                Pago.objects.create(
                    pedido=pedido,
                    metodo=form.cleaned_data['metodo_pago'],
                    nombre_referencia=form.cleaned_data.get('nombre_referencia', ''),
                )

                carrito.vaciar()
            return redirect('frontend:pedido_confirmado', pedido_id=pedido.id)
    else:
        form = CheckoutForm(usuario=request.user)

    return render(request, 'frontend/checkout.html', {
        'form': form,
        'items': items,
        'total': carrito.total(),
    })


@login_required(login_url='frontend:login')
def pedido_confirmado(request, pedido_id):
    from catalogo.models import ConfiguracionNegocio
    pedido = get_object_or_404(Pedido, pk=pedido_id, clienta=request.user)
    config = ConfiguracionNegocio.obtener()
    return render(request, 'frontend/pedido_confirmado.html', {
        'pedido': pedido,
        'config_negocio': config,
    })

@login_required(login_url='frontend:login')
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(clienta=request.user).prefetch_related('items', 'pago')
    return render(request, 'frontend/mis_pedidos.html', {'pedidos': pedidos})


@login_required(login_url='frontend:login')
def gestionar_direcciones(request):
    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.usuario = request.user
            direccion.save()
            messages.success(request, "Dirección guardada.")
            return redirect('frontend:direcciones')
    else:
        form = DireccionForm()

    direcciones = request.user.direcciones.all()
    return render(request, 'frontend/direcciones.html', {'form': form, 'direcciones': direcciones})

@login_required(login_url='frontend:login')
def pedido_detalle(request, pedido_id):
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related('items', 'pago'), pk=pedido_id, clienta=request.user
    )
    if pedido.notificacion_entrega_pendiente:
        pedido.notificacion_entrega_pendiente = False
        pedido.save(update_fields=['notificacion_entrega_pendiente'])

    pasos = ['confirmado', 'preparacion', 'entregado']
    paso_actual = pasos.index(pedido.estado) if pedido.estado in pasos else 0
    return render(request, 'frontend/pedido_detalle.html', {
        'pedido': pedido,
        'pasos': pasos,
        'paso_actual': paso_actual,
    })

@user_passes_test(lambda u: u.is_staff, login_url='frontend:login')
def resumen_ventas(request):
    hoy = timezone.localtime(timezone.now())
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if hoy.month == 12:
        fin_mes = inicio_mes.replace(year=hoy.year + 1, month=1)
    else:
        fin_mes = inicio_mes.replace(month=hoy.month + 1)

    pedidos_mes = Pedido.objects.filter(
        creado__gte=inicio_mes, creado__lt=fin_mes
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

    return render(request, 'frontend/resumen_ventas.html', {
        'total_pedidos': total_pedidos,
        'monto_total': monto_total,
        'entregados': entregados,
        'por_metodo': por_metodo,
        'mes_actual': hoy.strftime('%B %Y'),
    })