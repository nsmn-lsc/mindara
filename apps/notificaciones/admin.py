"""
Configuración del panel de administración para notificaciones
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Notificacion, NotificacionLeida


class NotificacionLeidaInline(admin.TabularInline):
    """Inline para mostrar quién ha leído la notificación"""
    model = NotificacionLeida
    extra = 0
    readonly_fields = ('usuario', 'fecha_lectura')
    can_delete = False


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    """Administración de notificaciones"""
    
    list_display = [
        'titulo', 'tipo', 'prioridad', 'get_creado_por',
        'get_nivel_usuario_objetivo', 'fecha_creacion', 
        'fecha_expiracion', 'get_lecturas_count'
    ]
    
    list_filter = [
        'tipo', 'prioridad', 'nivel_usuario_objetivo',
        'fecha_creacion', 'fecha_expiracion'
    ]
    
    search_fields = [
        'titulo', 'mensaje', 'creado_por__username',
        'creado_por__first_name', 'creado_por__last_name'
    ]
    
    readonly_fields = [
        'fecha_creacion', 'get_lecturas_count'
    ]
    
    filter_horizontal = ['usuarios_objetivo']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'mensaje', 'tipo', 'prioridad')
        }),
        ('Destinatarios', {
            'fields': ('nivel_usuario_objetivo', 'usuarios_objetivo'),
            'description': 'Define quién recibirá esta notificación'
        }),
        ('Configuración', {
            'fields': ('fecha_expiracion',),
            'classes': ('collapse',)
        }),
        ('Información del sistema', {
            'fields': ('fecha_creacion', 'get_lecturas_count'),
            'classes': ('collapse',),
            'description': 'Información automática del sistema'
        }),
    )
    
    inlines = [NotificacionLeidaInline]
    
    def get_creado_por(self, obj):
        """Muestra información del creador de la notificación"""
        if obj.creado_por:
            return f"{obj.creado_por.get_full_name() or obj.creado_por.username}"
        return "Sistema"
    get_creado_por.short_description = "Creado por"
    
    def get_nivel_usuario_objetivo(self, obj):
        """Muestra el nivel de usuario objetivo con color"""
        if obj.nivel_usuario_objetivo:
            colors = {
                'ADMIN': '#dc3545',
                'MANAGER': '#fd7e14',
                'USER': '#28a745'
            }
            color = colors.get(obj.nivel_usuario_objetivo, '#6c757d')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                obj.get_nivel_usuario_objetivo_display()
            )
        return "Usuarios específicos"
    get_nivel_usuario_objetivo.short_description = "Dirigida a"
    
    def get_lecturas_count(self, obj):
        """Muestra el número de lecturas"""
        count = obj.lecturas.count()
        if count > 0:
            url = reverse('admin:notificaciones_notificacionleida_changelist')
            return format_html(
                '<a href="{}?notificacion__id__exact={}" target="_blank">{} lecturas</a>',
                url, obj.pk, count
            )
        return "Sin lecturas"
    get_lecturas_count.short_description = "Lecturas"
    
    def save_model(self, request, obj, form, change):
        """Guardar el modelo asignando el usuario creador"""
        if not change:  # Solo en creación
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(NotificacionLeida)
class NotificacionLeidaAdmin(admin.ModelAdmin):
    """Administración de lecturas de notificaciones"""
    
    list_display = [
        'get_notificacion_titulo', 'get_usuario_info',
        'fecha_lectura'
    ]
    
    list_filter = [
        'fecha_lectura', 'notificacion__tipo',
        'notificacion__prioridad', 'usuario__user_level'
    ]
    
    search_fields = [
        'notificacion__titulo', 'usuario__username',
        'usuario__first_name', 'usuario__last_name'
    ]
    
    readonly_fields = ['notificacion', 'usuario', 'fecha_lectura']
    
    def get_notificacion_titulo(self, obj):
        """Muestra el título de la notificación"""
        return obj.notificacion.titulo
    get_notificacion_titulo.short_description = "Notificación"
    
    def get_usuario_info(self, obj):
        """Muestra información del usuario"""
        user = obj.usuario
        return f"{user.get_full_name() or user.username} ({user.get_user_level_display()})"
    get_usuario_info.short_description = "Usuario"
    
    def has_add_permission(self, request):
        """No permitir agregar manualmente lecturas"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar lecturas"""
        return False
