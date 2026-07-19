from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalogo.models import Categoria, Producto, ConfiguracionNegocio
from django.db import transaction
from .carrito import Carrito
from .forms_checkout import DireccionForm, CheckoutForm
from pedidos.models import Pedido, ItemPedido, Pago
import qrcode
import io, base64
from catalogo.models import Categoria, Producto
from clientas.models import PerfilCliente, Favorito
from .forms import RegistroForm, PerfilForm


def inicio(request):
    return render(request, 'frontend/inicio.html')


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
        if perfil_cliente and perfil_cliente.talla_calzon:
            productos = productos.filter(talla=perfil_cliente.talla_calzon)

            
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    if talla:
        productos = productos.filter(talla=talla)
    if color:
        productos = productos.filter(color__iexact=color)

    colores_disponibles = (
        Producto.objects.filter(activo=True)
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
            messages.success(request, "¡Registro exitoso! Bienvenida.")
            return redirect('frontend:perfil')
    else:
        form = RegistroForm()
    return render(request, 'frontend/registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
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
    siguiente = request.POST.get('siguiente') or 'frontend:catalogo'
    return redirect(siguiente)
def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        talla = request.POST.get('talla', 'UNICA')
        cantidad = int(request.POST.get('cantidad', 1))
        carrito = Carrito(request)
        carrito.agregar(producto_id, talla, cantidad)
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
                pedido = Pedido.objects.create(
                    clienta=request.user,
                    direccion=form.cleaned_data['direccion'] if form.cleaned_data['tipo_entrega'] == 'domicilio' else None,
                    tipo_entrega=form.cleaned_data['tipo_entrega'],
                    nota=form.cleaned_data['nota'],
                )
                for item in items:
                    ItemPedido.objects.create(
                        pedido=pedido,
                        producto=item['producto'],
                        talla=item['talla'],
                        cantidad=item['cantidad'],
                        precio_unitario=item['producto'].precio_final,
                    )
                pedido.recalcular_total()

                Pago.objects.create(
                    pedido=pedido,
                    metodo=form.cleaned_data['metodo_pago'],
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
    pedido = get_object_or_404(Pedido, pk=pedido_id, clienta=request.user)
    qr_base64 = None
    if pedido.pago.metodo == 'qr':
        from catalogo.models import ConfiguracionNegocio
        config = ConfiguracionNegocio.obtener()
        texto = f"Pedido #{pedido.id} - Monto: Bs {pedido.total} - Cuenta: {config.banco_numero_cuenta}"
        img = qrcode.make(texto)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    return render(request, 'frontend/pedido_confirmado.html', {'pedido': pedido, 'qr_base64': qr_base64})

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