from django.urls import path
from apps.accesos.views import validar_pin, dashboard_accesos
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import resumen_por_usuario, resumen_dinamico, eventos_recientes, eventos_historial, contador_alertas, panel_perfil

app_name = 'accesos'

urlpatterns = [
    path('pin/validar/', validar_pin, name='validar_pin'),
    path("eventos_recientes/", eventos_recientes, name="eventos_recientes"),
    path("eventos_historial/", eventos_historial, name="eventos_historial"),
    path('dashboard/', dashboard_accesos, name='dashboard_accesos'),
    path('resumen/', resumen_por_usuario, name='resumen_por_usuario'),
    path('generar_qr/<int:usuario_id>/', views.generar_qr, name='generar_qr'),
    path("resumen_dinamico/", views.resumen_dinamico, name="resumen_dinamico"),
    path("validar_qr/", views.validar_qr, name="validar_qr"),
    path('alertas/contador/', contador_alertas, name='contador_alertas'),
    path('perfil/panel/', panel_perfil, name='panel_perfil'),
    path("evento/<int:evento_id>/visto/", views.marcar_evento_visto, name="marcar_evento_visto"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)