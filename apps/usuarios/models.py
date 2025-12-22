from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone


class Usuario(AbstractUser):
    pin = models.CharField(max_length=10, unique=True, blank=True, null=True)

    rol = models.CharField(max_length=20, choices=[
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
        ('visitante', 'Visitante')
    ])

    horario_inicio = models.TimeField(null=True, blank=True)
    horario_fin = models.TimeField(null=True, blank=True)

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    qr_token = models.CharField(max_length=100, blank=True, null=True)
    qr_created_at = models.DateTimeField(blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.qr_token:
            self.qr_token = str(uuid.uuid4())
            self.qr_created_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.rol})"
