"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect


# --- Redirección raíz ---
# Si el usuario NO está autenticado → Login
# Si está autenticado → Dashboard
def root_redirect(request):
    if request.user.is_authenticated:
        return redirect("accesos:dashboard")
    return redirect("usuarios:login")


urlpatterns = [

    # Admin
    path("admin/", admin.site.urls),

    # Apps internas
    path("accesos/", include(("apps.accesos.urls", "accesos"), namespace="accesos")),
    path("usuarios/", include(("apps.usuarios.urls", "usuarios"), namespace="usuarios")),

    # Logout
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/usuarios/login/"),
        name="logout"
    ),

    # Raíz del sitio
    path("", root_redirect),
]


# --- Archivos estáticos y media en modo DEBUG ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
