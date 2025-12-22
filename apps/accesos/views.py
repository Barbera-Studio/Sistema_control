from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Count, Value
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from apps.accesos.models import EventoAcceso
from apps.usuarios.models import Usuario
from datetime import timedelta
import qrcode
from io import BytesIO
import base64
import uuid
import hmac, hashlib
from django.conf import settings
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from .models import EventoAcceso


# 🔐 Validación con PIN
def validar_pin(request):
    if request.method == "POST":
        pin = request.POST.get("pin")
        usuario = Usuario.objects.filter(pin=pin).first()
        hora_actual = timezone.localtime().time()

        # Registro del evento
        if not usuario:
            EventoAcceso.objects.create(usuario=None, resultado="denegado")
            return render(request, "accesos/partials/acceso_denegado.html", {
                "motivo": "PIN inválido",
                "hx_trigger": "actualizar-panel"  # ✅ dispara actualización
            })

        if usuario.horario_inicio and usuario.horario_fin:
            if usuario.horario_inicio <= hora_actual <= usuario.horario_fin:
                EventoAcceso.objects.create(usuario=usuario, resultado="permitido")
                return render(request, "accesos/partials/acceso_autorizado.html", {
                    "usuario": usuario,
                    "hx_trigger": "actualizar-panel"  # ✅ dispara actualización
                })
            else:
                EventoAcceso.objects.create(usuario=usuario, resultado="fuera de horario")
                return render(request, "accesos/partials/acceso_denegado.html", {
                    "motivo": "Fuera de horario",
                    "hx_trigger": "actualizar-panel"  # ✅ dispara actualización
                })
        else:
            EventoAcceso.objects.create(usuario=usuario, resultado="denegado")
            return render(request, "accesos/partials/acceso_denegado.html", {
                "motivo": "Horario no configurado",
                "hx_trigger": "actualizar-panel"  # ✅ dispara actualización
            })

    # Si no es POST, redirige al dashboard completo
    return redirect('dashboard_accesos')


from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Value
from django.db.models.functions import Coalesce
from datetime import timedelta

from apps.accesos.models import EventoAcceso

# 📊 Dashboard de accesos
def dashboard_accesos(request):
    # 🕒 Últimos 50 eventos
    eventos = EventoAcceso.objects.select_related('usuario').order_by('-fecha')[:50]

    # 🧑‍🚀 Distribución por rol
    roles_raw = EventoAcceso.objects.annotate(
        rol_nombre=Coalesce('usuario__rol', Value('Desconocido'))
    ).values('rol_nombre').annotate(total=Count('id'))

    roles = [
        {
            "rol_nombre": r["rol_nombre"],
            "total": r["total"],
            "x": 20 + i * 40,
            "height": r["total"],
            "y": max(0, 100 - r["total"])
        }
        for i, r in enumerate(roles_raw)
    ]

    # 🚦 Distribución por resultado
    resultados_raw = EventoAcceso.objects.values('resultado').annotate(total=Count('id'))

    resultados = [
        {
            "resultado": r["resultado"],
            "total": r["total"],
            "x": 20 + i * 40,
            "height": r["total"],
            "y": max(0, 100 - r["total"])
        }
        for i, r in enumerate(resultados_raw)
    ]

    # 🔔 Últimas alertas críticas
    hace_24_horas = timezone.now() - timedelta(hours=24)
    alertas = EventoAcceso.objects.filter(
        resultado__in=['denegado', 'fuera de horario'],
        fecha__gte=hace_24_horas
    ).select_related('usuario').order_by('-fecha')[:5]

    # 🚀 Render orbital
    return render(request, 'accesos/panel.html', {
        'eventos': eventos,
        'roles': roles,
        'resultados': resultados,
        'alertas': alertas,
        'now': timezone.localtime()
    })


# 📜 Eventos recientes (auto-refresh con HTMX)
def eventos_recientes(request):
    alertas = EventoAcceso.objects.filter(visto=False)[:50]  # solo no vistos
    return render(request, "accesos/partials/eventos_fragmento.html", {"alertas": alertas})


def contador_alertas(request):
    hace_24_horas = timezone.now() - timedelta(hours=24)
    total = EventoAcceso.objects.filter(
        resultado__in=['denegado', 'fuera de horario'],
        fecha__gte=hace_24_horas,
        visto=False                
    ).count()

    if total > 0:
        html = f'''
        <span class="absolute -top-2 -right-2 bg-red-600 text-white text-xs px-2.5 py-1.5 rounded-full font-bold 
                     animate-[alertaPulse_1.5s_infinite] shadow-md">
          {total}
        </span>
        '''
        return HttpResponse(html)
    else:
        return HttpResponse("")
    

def eventos_historial(request):
    eventos = EventoAcceso.objects.select_related('usuario').order_by('-fecha')[:50]
    return render(request, 'accesos/partials/eventos_historial.html', {'eventos': eventos})

# 🧾 Resumen por usuario
def resumen_por_usuario(request):
    resumen = EventoAcceso.objects.values('usuario__username', 'resultado').annotate(total=Count('id'))
    return render(request, 'accesos/resumen.html', {'resumen': resumen})


# 📷 Validación con QR
@csrf_exempt
def validar_qr(request):
    token = request.POST.get('qr_token')
    usuario = Usuario.objects.filter(qr_token=token).first()

    if not usuario:
        EventoAcceso.objects.create(usuario=None, resultado="denegado")
        return render(request, 'accesos/partials/acceso_denegado.html', {'motivo': 'QR inválido'})

    if not usuario.qr_created_at or usuario.qr_created_at < timezone.now() - timedelta(hours=24):
        EventoAcceso.objects.create(usuario=usuario, resultado="denegado")
        return render(request, 'accesos/partials/acceso_denegado.html', {'motivo': 'QR expirado'})

    EventoAcceso.objects.create(usuario=usuario, resultado="permitido")
    return render(request, 'accesos/partials/acceso_autorizado.html', {'usuario': usuario})


# 🕹 Vista futurista principal
def acceso_futurista(request):
    hace_24h = timezone.now() - timedelta(hours=24)
    ultimo_evento = EventoAcceso.objects.filter(fecha__gte=hace_24h).order_by('-fecha').first()

    return render(request, 'accesos/acceso.html', {
        'usuario_reciente': ultimo_evento.usuario if ultimo_evento else None,
        'now': timezone.localtime()
    })


# 🧾 Generación de QR
def generar_qr(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Regenerar si han pasado más de 24h
    if not usuario.qr_created_at or usuario.qr_created_at < timezone.now() - timedelta(days=1):
        usuario.qr_token = str(uuid.uuid4())
        usuario.qr_created_at = timezone.now()
        usuario.save()

    qr = qrcode.make(usuario.qr_token)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "accesos/qr.html", {"usuario": usuario, "qr_base64": qr_base64})


# 🔐 Firma de seguridad para QR API
def generar_firma(usuario):
    clave_secreta = settings.QR_SECRET_KEY.encode()
    mensaje = f"{usuario.id}:{usuario.qr_token}".encode()
    return hmac.new(clave_secreta, mensaje, hashlib.sha256).hexdigest()


def registrar_evento(usuario, resultado="validación externa"):
    EventoAcceso.objects.create(usuario=usuario, resultado=resultado)


# 🌐 API REST para validación QR
@api_view(['POST'])
def validar_qr_api(request):
    token = request.data.get("qr_token")
    firma = request.data.get("firma")
    pin = request.data.get("pin")

    usuario = Usuario.objects.filter(qr_token=token).first()
    if not usuario:
        return Response({"status": "denegado"}, status=403)

    if generar_firma(usuario) != firma or usuario.pin != pin:
        registrar_evento(usuario, resultado="denegado")
        return Response({"status": "denegado"}, status=403)

    registrar_evento(usuario, resultado="permitido")
    return Response({"status": "acceso concedido"})


from django.shortcuts import render
from django.db.models import Count, Value
from django.db.models.functions import Coalesce
from .models import EventoAcceso
from django.utils.safestring import mark_safe
import json


def resumen_dinamico(request):
    # 🧾 Últimos eventos
    eventos = list(EventoAcceso.objects.select_related('usuario').order_by('-fecha')[:50])

    # 🔷 Conteo por rol (con fallback "Desconocido")
    roles_raw = (
        EventoAcceso.objects
        .annotate(rol_nombre=Coalesce('usuario__rol', Value('Desconocido')))
        .values('rol_nombre')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # 🟢 Conteo por resultado
    resultados_raw = (
        EventoAcceso.objects
        .values('resultado')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # 📊 Escala máxima para SVG
    max_total = max(
        [r["total"] for r in roles_raw] + [r["total"] for r in resultados_raw],
        default=1
    )

    # 📐 Generar barras SVG
    def generar_barras(data, spacing=220, base_x=110, max_height=300, base_y=340):
        barras = []
        for i, r in enumerate(data):
            height = int((r["total"] / max_total) * max_height)
            barras.append({
                "label": r.get("rol_nombre") or r.get("resultado"),
                "total": r["total"],
                "x": base_x + i * spacing,
                "height": height,
                "y": base_y - height
            })
        return barras

    escala_y = [{"valor": i, "y": 560 - i} for i in range(0, 501, 100)]

    roles_svg = generar_barras(roles_raw)
    resultados_svg = generar_barras(resultados_raw)

    leyenda_roles = [
        {"label": r["label"], "color_id": i + 1, "y": 60 + i * 30}
        for i, r in enumerate(roles_svg)
    ]

    leyenda_resultados = [
        {"label": r["label"], "color_id": i + 1, "y": 60 + i * 30}
        for i, r in enumerate(resultados_svg)
    ]

    # 📊 Datos para Chart.js (JSON seguro para inyección en template)
    datos_usuarios = {
        "labels": [r["rol_nombre"] for r in roles_raw],
        "valores": [r["total"] for r in roles_raw]
    }

    datos_accesos = {
        "labels": [r["resultado"] for r in resultados_raw],
        "valores": [r["total"] for r in resultados_raw]
    }

    return render(request, "accesos/partials/resumen_dinamico.html", {
        "eventos": eventos,
        "roles": roles_raw,
        "resultados": resultados_raw,
        "roles_svg": roles_svg,
        "resultados_svg": resultados_svg,
        "escala_y": escala_y,
        "leyenda_roles": leyenda_roles,
        "leyenda_resultados": leyenda_resultados,
        "datos_usuarios_json": mark_safe(json.dumps(datos_usuarios)),
        "datos_accesos_json": mark_safe(json.dumps(datos_accesos)),
    })

@login_required
def panel_perfil(request):
    eventos_usuario = EventoAcceso.objects.select_related('usuario')\
        .filter(usuario=request.user).order_by('-fecha')[:10]
    return render(request, 'accesos/partials/perfil_fragmento.html', {
        'eventos_usuario': eventos_usuario
    })


@require_POST
def marcar_evento_visto(request, evento_id):
    evento = get_object_or_404(EventoAcceso, id=evento_id)
    evento.visto = True
    evento.save(update_fields=["visto"])
    return HttpResponse("")  
