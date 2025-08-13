from django.contrib import admin
from .models import CategoriaEvento, Evento


@admin.register(CategoriaEvento)
class CategoriaEventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'color', 'activa', 'created_at')
    list_filter = ('activa', 'created_at')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'color', 'activa')
        }),
    )


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre_evento', 'usuario', 'fecha_evento', 'hora_evento', 'etapa', 'prioridad', 'aforo')
    list_filter = ('etapa', 'prioridad', 'fecha_evento', 'carpeta_ejecutiva', 'marca_temporal')
    search_fields = ('nombre_evento', 'objetivo', 'sede', 'participantes')
    date_hierarchy = 'fecha_evento'
    ordering = ('-fecha_evento', '-hora_evento')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre_evento', 'objetivo', 'usuario')
        }),
        ('Fecha y Horario', {
            'fields': ('fecha_evento', 'hora_evento', 'duracion', 'duracion_personalizada')
        }),
        ('Ubicación y Logística', {
            'fields': ('sede', 'link_maps', 'aforo', 'participantes')
        }),
        ('Gestión del Evento', {
            'fields': ('etapa', 'prioridad')
        }),
        ('Carpeta Ejecutiva', {
            'fields': ('carpeta_ejecutiva', 'carpeta_ejecutiva_liga'),
            'classes': ('collapse',)
        }),
        ('Seguimiento', {
            'fields': ('compromisos', 'observaciones'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('usuario', 'marca_temporal')
        return ('marca_temporal',)
    
    def save_model(self, request, obj, form, change):
        if not change:  # if creating new object
            obj.usuario = request.user
        super().save_model(request, obj, form, change)
