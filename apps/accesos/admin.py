from django.contrib import admin
from .models import EventoAcceso

@admin.register(EventoAcceso)
class EventoAccesoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'resultado')
    list_filter = ('resultado', 'fecha')
    search_fields = ('usuario__username',)

    date_hierarchy = 'fecha'

