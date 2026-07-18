from django.urls import path
from .views import CategoriaListaView, ProductoListaView, ProductoDetalleView, whatsapp_contacto

urlpatterns = [
    path('categorias/', CategoriaListaView.as_view(), name='categoria-lista'),
    path('productos/', ProductoListaView.as_view(), name='producto-lista'),
    path('productos/<int:pk>/', ProductoDetalleView.as_view(), name='producto-detalle'),
    path('whatsapp/', whatsapp_contacto, name='whatsapp-contacto'),
]