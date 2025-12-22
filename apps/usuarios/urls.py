# apps/usuarios/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    editar_avatar,
    actualizar_perfil,
    login_view,
    dashboard_view,
    cerrar_sesion,
)

app_name = "usuarios"

urlpatterns = [
    # Perfil y autenticación propia
    path("editar-avatar/", editar_avatar, name="editar_avatar"),
    path("actualizar-perfil/", actualizar_perfil, name="actualizar_perfil"),
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("logout/", cerrar_sesion, name="logout"),

    # Recuperación de credenciales (flujo estándar y seguro de Django)
    path(
        "recuperar/",
        auth_views.PasswordResetView.as_view(
            template_name="usuarios/recuperar.html",
            email_template_name="usuarios/email_recuperar.html",
            html_email_template_name="usuarios/email_recuperar.html",
            subject_template_name="usuarios/email_recuperar_subject.txt",
            success_url="/usuarios/recuperar/enviado/",
        ),
        name="password_reset",
    ),
    path(
        "recuperar/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="usuarios/recuperar_enviado.html",
        ),
        name="password_reset_done",
    ),
    path(
        "recuperar/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="usuarios/recuperar_confirmacion.html",
            success_url="/usuarios/recuperar/completo/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "recuperar/completo/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="usuarios/recuperar_completo.html",
        ),
        name="password_reset_complete",
    ),
]
