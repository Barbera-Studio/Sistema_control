from django.db import models
from apps.usuarios.models import Usuario
from django.conf import settings


class EventoAcceso(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="eventos_acceso"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    resultado = models.CharField(max_length=50, blank=True, null=True)
    visto = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        u = self.usuario.username if self.usuario else "Desconocido"
        return f"{u} · {self.resultado or 'evento'} · {self.fecha:%Y-%m-%d %H:%M:%S}"