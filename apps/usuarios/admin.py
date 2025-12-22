from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('username', 'rol', 'horario_inicio', 'horario_fin', 'avatar_preview')
    readonly_fields = ('avatar_preview',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email', 'avatar')}),
        ('Datos de acceso', {'fields': ('pin', 'rol', 'horario_inicio', 'horario_fin')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" style="height:50px;border-radius:50%;">'
        return "Sin avatar"
    avatar_preview.allow_tags = True
    avatar_preview.short_description = "Avatar"


