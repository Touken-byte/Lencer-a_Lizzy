from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegistroClienteView, PerfilClienteView, FavoritoListaCrearView, FavoritoEliminarView

urlpatterns = [
    # Autenticación (login con username/password, devuelve tokens JWT)
    path('login/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # HU-24
    path('registro/', RegistroClienteView.as_view(), name='registro-cliente'),
    path('perfil/', PerfilClienteView.as_view(), name='perfil-cliente'),

    # HU-25
    path('favoritos/', FavoritoListaCrearView.as_view(), name='favoritos'),
    path('favoritos/<int:producto_id>/', FavoritoEliminarView.as_view(), name='favorito-eliminar'),
]