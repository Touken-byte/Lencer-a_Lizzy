from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Mensaje


class MensajesInline(admin.TabularInline):
    model = Mensaje
    extra = 0
    readonly_fields = ('emisor', 'texto', 'imagen', 'leido', 'creado')
    can_delete = False


class UserAdminConMensajes(UserAdmin):
    list_display = UserAdmin.list_display + ('mensajes_sin_leer',)

    @admin.display(description='Mensajes sin leer')
    def mensajes_sin_leer(self, obj):
        cantidad = Mensaje.objects.filter(usuario=obj, emisor='clienta', leido=False).count()
        if cantidad > 0:
            return f"🔴 {cantidad}"
        return "—"


admin.site.unregister(User)
admin.site.register(User, UserAdminConMensajes)


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'emisor', 'texto', 'leido', 'creado')
    list_filter = ('emisor', 'leido')
    search_fields = ('usuario__username', 'texto')

    def has_add_permission(self, request):
        return False

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if 'emisor' in fields:
            fields.remove('emisor')
        return fields

    def save_model(self, request, obj, form, change):
        obj.emisor = 'vendedora'
        super().save_model(request, obj, form, change)
