from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from .forms import AvatarForm
from .models import Usuario
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.http import urlencode
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.core.mail import send_mail
import uuid
from django.utils.crypto import get_random_string


@login_required
def editar_avatar(request):
    usuario = request.user

    if request.method == 'POST' and request.FILES.get('avatar'):
        avatar = request.FILES['avatar']
        usuario.avatar = avatar
        usuario.save()
        messages.success(request, '✅ Avatar actualizado correctamente.')
        return redirect('dashboard_accesos')

    return render(request, 'usuarios/editar_avatar.html', {'rango': range(20)})


@csrf_exempt
def actualizar_perfil(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        username = request.POST.get('username')
        rol = request.POST.get('rol')
        inicio = request.POST.get('horario_inicio')
        fin = request.POST.get('horario_fin')

        try:
            usuario = Usuario.objects.get(id=user_id)
            usuario.username = username
            usuario.rol = rol
            usuario.horario_inicio = inicio
            usuario.horario_fin = fin
            usuario.save()
            return JsonResponse({'status': 'ok'})
        except Usuario.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado'})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('accesos:dashboard_accesos')
        else:
            error = "Credenciales inválidas"
    else:
        error = None

    # Si la petición viene de HTMX → devolver solo el fragmento
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'usuarios/partials/login_form.html', {'error': error})

    # Si es navegación normal → devolver la página completa
    return render(request, 'usuarios/login.html', {'error': error, 'rango': range(20)})



def dashboard_view(request):
    return render(request, 'usuarios/dashboard.html')

def recuperar_acceso_view(request):
    """
    GET: muestra la página de recuperación
    POST: genera un enlace y lo muestra en la misma vista, o redirige a confirmación
    """
    contexto = {}

    if request.method == "POST":
        # Genera un token sencillo (ajústalo a tu lógica real)
        token = get_random_string(32)
        # Construye un enlace (ajústalo al dominio real o a una vista que valide el token)
        enlace = request.build_absolute_uri(f"/usuarios/recuperar/confirmacion/?token={token}")

        # Opción A: Mostrar el enlace en esta misma página
        contexto["enlace_generado"] = enlace
        messages.success(request, "Se ha generado tu enlace de recuperación.")

        # Opción B: Redirigir a la página de confirmación (descomenta si prefieres redirigir)
        # return redirect(reverse("usuarios:confirmar_recuperacion") + f"?token={token}")

    return render(request, "usuarios/recuperar.html", contexto)


def confirmar_recuperacion_view(request):
    """
    Página de confirmación de recuperación: recibe ?token=... y muestra estado.
    Implementa aquí la validación del token si lo necesitas.
    """
    token = request.GET.get("token")
    if not token:
        messages.error(request, "Token de recuperación no válido o ausente.")
        ctx = {"token_valido": False}
    else:
        # Aquí validarías el token en BD, caducidad, etc.
        ctx = {"token_valido": True, "token": token}
        messages.success(request, "Token validado. Sigue las instrucciones para restablecer tu acceso.")

    return render(request, "usuarios/recuperar_confirmacion.html", ctx)

def cerrar_sesion(request):
    logout(request)
    return redirect('/usuarios/login/')