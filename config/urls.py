from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from frontend.admin_views import salir_admin, resumen_ventas_admin
from chat.admin_views import admin_panel_chats, admin_chat_detalle, admin_notificacion_masiva

urlpatterns = [
    path('admin/salir/', salir_admin, name='admin_logout_custom'),
    path('admin/chats/', admin_panel_chats, name='admin_panel_chats'),
    path('admin/chats/notificar/', admin_notificacion_masiva, name='admin_notificacion_masiva'),
    path('admin/chats/<int:usuario_id>/', admin_chat_detalle, name='admin_chat_detalle'),
    path('admin/ventas/', resumen_ventas_admin, name='admin_resumen_ventas'),
    path('admin/', admin.site.urls),
    path('api/catalogo/', include('catalogo.urls')),
    path('api/clientas/', include('clientas.urls')),
    path('', include('frontend.urls')),
    path('chat/', include('chat.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
