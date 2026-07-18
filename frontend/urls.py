from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('catalogo/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('favoritos/', views.favoritos_lista, name='favoritos'),
    path('favoritos/<int:producto_id>/toggle/', views.favorito_toggle, name='favorito_toggle'),

    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/actualizar/<str:clave>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<str:clave>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedido/<int:pedido_id>/confirmado/', views.pedido_confirmado, name='pedido_confirmado'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('direcciones/', views.gestionar_direcciones, name='direcciones'),
]
