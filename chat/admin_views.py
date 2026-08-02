from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin import site
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.db.models import Max

from .models import Mensaje, ImagenMensaje
from .forms import MensajeForm


@staff_member_required
def admin_panel_chats(request):
    usuarios_ids = (
        Mensaje.objects.values('usuario')
        .annotate(ultimo=Max('creado'))
        .order_by('-ultimo')
        .values_list('usuario', flat=True)
    )
    usuarios = User.objects.filter(id__in=usuarios_ids)

    conversaciones = []
    for usuario in usuarios:
        no_leidos = Mensaje.objects.filter(usuario=usuario, emisor='clienta', leido=False).count()
        ultimo_mensaje = Mensaje.objects.filter(usuario=usuario).order_by('-creado').first()
        conversaciones.append({
            'usuario': usuario,
            'no_leidos': no_leidos,
            'ultimo_mensaje': ultimo_mensaje,
        })
    conversaciones.sort(key=lambda c: c['ultimo_mensaje'].creado, reverse=True)

    context = {
        **site.each_context(request),
        'title': 'Bandeja de chats',
        'conversaciones': conversaciones,
    }
    return render(request, 'admin/chat/panel_chats.html', context)


@staff_member_required
def admin_chat_detalle(request, usuario_id):
    usuario = get_object_or_404(User, pk=usuario_id)
    mensajes = Mensaje.objects.filter(usuario=usuario)
    mensajes.filter(emisor='clienta', leido=False).update(leido=True)

    if request.method == 'POST':
        form = MensajeForm(request.POST, request.FILES)
        if form.is_valid():
            mensaje = Mensaje.objects.create(
                usuario=usuario, emisor='vendedora',
                texto=form.cleaned_data.get('texto', ''),
                video=form.cleaned_data.get('video')
            )
            for img in request.FILES.getlist('imagenes'):
                ImagenMensaje.objects.create(mensaje=mensaje, imagen=img)
            return redirect('admin_chat_detalle', usuario_id=usuario.id)
    else:
        form = MensajeForm()

    context = {
        **site.each_context(request),
        'title': f'Chat con {usuario.username}',
        'usuario': usuario,
        'mensajes': mensajes,
        'form': form,
    }
    return render(request, 'admin/chat/panel_chat_detalle.html', context)

@staff_member_required
def admin_notificacion_masiva(request):
    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if texto:
            clientas = User.objects.filter(is_staff=False)
            mensajes_creados = [
                Mensaje(usuario=clienta, emisor='vendedora', texto=texto, automatico=True)
                for clienta in clientas
            ]
            Mensaje.objects.bulk_create(mensajes_creados)
        return redirect('admin_panel_chats')

    context = {
        **site.each_context(request),
        'title': 'Notificar a todas las clientas',
    }
    return render(request, 'admin/chat/notificacion_masiva.html', context)