from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import PerfilCliente, Favorito
from .serializers import RegistroClienteSerializer, PerfilClienteSerializer, FavoritoSerializer


class RegistroClienteView(generics.CreateAPIView):
    """HU-24: crear perfil de clienta"""
    serializer_class = RegistroClienteSerializer
    permission_classes = [permissions.AllowAny]


class PerfilClienteView(generics.RetrieveUpdateAPIView):
    """HU-24: ver y editar mi perfil (datos editables)"""
    serializer_class = PerfilClienteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        perfil, _ = PerfilCliente.objects.get_or_create(usuario=self.request.user)
        return perfil


class FavoritoListaCrearView(generics.ListCreateAPIView):
    """HU-25: ver mis favoritos y agregar uno nuevo"""
    serializer_class = FavoritoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorito.objects.filter(usuario=self.request.user).select_related('producto')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class FavoritoEliminarView(APIView):
    """HU-25: quitar un producto de favoritos"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, producto_id):
        favorito = get_object_or_404(Favorito, usuario=request.user, producto_id=producto_id)
        favorito.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)