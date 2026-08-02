from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q, Max
from django.contrib import messages as django_messages
from django.contrib.auth.models import User
from .models import ImagenMensaje, Mensaje

from .forms import MensajeForm

def es_vendedora(user):
    return user.is_staff


@login_required(login_url='frontend:login')
def chat_clienta(request):
    """HU-16, HU-18: la clienta habla con la vendedora"""
    mensajes = Mensaje.objects.filter(usuario=request.user)
    mensajes.filter(emisor='vendedora', leido=False).update(leido=True)

    if request.method == 'POST':
        form = MensajeForm(request.POST, request.FILES)
        if form.is_valid():
            mensaje = Mensaje.objects.create(
                usuario=request.user,
                emisor='clienta',
                texto=form.cleaned_data.get('texto', ''),
                video=form.cleaned_data.get('video')
            )
            imagenes = request.FILES.getlist('imagenes')
            for img in imagenes:
                ImagenMensaje.objects.create(mensaje=mensaje, imagen=img)
            return redirect('chat:chat_clienta')
    else:
        initial = {}
        pedido_ref = request.GET.get('pedido')
        if pedido_ref:
            initial['texto'] = f"Hola, tengo una consulta sobre mi pedido #{pedido_ref}: "
        form = MensajeForm(initial=initial)

    return render(request, 'chat/chat_clienta.html', {
        'mensajes': mensajes,
        'form': form,
    })
