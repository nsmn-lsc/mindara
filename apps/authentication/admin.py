"""
Configuración del panel de administración Django para autenticación
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Configuración del admin para el modelo User personalizado
    """
    
    # Campos mostrados en la lista de usuarios
    list_display = [
        'email', 'username', 'get_full_name', 'user_level', 
        'is_active', 'is_staff', 'created_at', 'avatar_preview'
    ]
    
    # Filtros laterales
    list_filter = [
        'user_level', 'is_active', 'is_staff', 'is_superuser', 
        'date_joined', 'last_login'
    ]
    
    # Campos de búsqueda
    search_fields = ['email', 'username', 'first_name', 'last_name']
    
    # Ordenamiento por defecto
    ordering = ['-created_at']
    
    # Configuración de los fieldsets para el formulario de edición
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Información Personal'), {
            'fields': (
                'first_name', 'last_name', 'email', 'phone', 
                'avatar'
            )
        }),
        (_('Permisos y Nivel'), {
            'fields': (
                'user_level', 'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        (_('Fechas Importantes'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets para agregar nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'user_level', 'password1', 'password2'
            ),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ['created_at', 'updated_at', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        """Mostrar nombre completo en la lista"""
        return obj.get_full_name()
    get_full_name.short_description = 'Nombre Completo'
    
    def avatar_preview(self, obj):
        """Mostrar miniatura del avatar"""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%;" />',
                obj.avatar.url
            )
        return "Sin avatar"
    avatar_preview.short_description = 'Avatar'
    
    def get_queryset(self, request):
        """
        Filtrar usuarios según el nivel del admin autenticado
        """
        qs = super().get_queryset(request)
        
        # Solo superusuarios pueden ver todos los usuarios
        if request.user.is_superuser:
            return qs
        
        # Admins pueden ver usuarios de nivel inferior
        if hasattr(request.user, 'user_level') and request.user.is_admin():
            return qs.exclude(is_superuser=True)
        
        # Otros solo pueden ver usuarios básicos
        return qs.filter(user_level='USER')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo UserProfile
    """
    
    list_display = [
        'user', 'location', 'website', 'birth_date',
        'notifications_email', 'notifications_push'
    ]
    
    list_filter = [
        'privacy_email', 'privacy_phone', 
        'notifications_email', 'notifications_push',
        'created_at'
    ]
    
    search_fields = [
        'user__email', 'user__username', 'user__first_name', 
        'user__last_name', 'location'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Información del Perfil'), {
            'fields': (
                'user', 'bio', 'location', 'website', 'birth_date'
            )
        }),
        (_('Configuraciones de Privacidad'), {
            'fields': ('privacy_email', 'privacy_phone'),
            'classes': ('collapse',)
        }),
        (_('Configuraciones de Notificaciones'), {
            'fields': ('notifications_email', 'notifications_push'),
            'classes': ('collapse',)
        }),
        (_('Fechas'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Filtrar perfiles según el nivel del admin
        """
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'user_level') and request.user.is_admin():
            return qs.exclude(user__is_superuser=True)
        
        return qs.filter(user__user_level='USER')


# Personalizar el título del admin
admin.site.site_header = "Mindara - Panel de Administración"
admin.site.site_title = "Mindara Admin"
admin.site.index_title = "Gestión del Sistema"
