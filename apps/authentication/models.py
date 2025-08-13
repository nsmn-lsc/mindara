"""
Modelos de autenticación para Mindara
Sistema de usuarios con 3 niveles de acceso
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser
    Incluye 3 niveles de usuario: ADMIN, MANAGER, USER
    """
    
    # Definición de los 3 niveles de usuario
    USER_LEVELS = [
        ('ADMIN', _('Administrador')),      # Nivel 1: Acceso completo al sistema
        ('MANAGER', _('Gestor')),           # Nivel 2: Gestión de contenido y usuarios básicos
        ('USER', _('Usuario')),             # Nivel 3: Acceso básico, solo lectura
    ]
    
    # Campos adicionales del usuario
    email = models.EmailField(
        _('email address'), 
        unique=True,
        help_text=_('Email único para cada usuario')
    )
    
    user_level = models.CharField(
        max_length=10,
        choices=USER_LEVELS,
        default='USER',
        verbose_name=_('Nivel de usuario'),
        help_text=_('Nivel de acceso del usuario en el sistema')
    )
    
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name=_('Teléfono'),
        help_text=_('Número de teléfono del usuario')
    )
    
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True,
        verbose_name=_('Avatar'),
        help_text=_('Imagen de perfil del usuario')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activo'),
        help_text=_('Indica si el usuario está activo en el sistema')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )
    
    # Configuración del campo email como identificador único
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.email}) - {self.get_user_level_display()}"
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.user_level == 'ADMIN'
    
    def is_manager(self):
        """Verifica si el usuario es gestor"""
        return self.user_level == 'MANAGER'
    
    def is_basic_user(self):
        """Verifica si el usuario es básico"""
        return self.user_level == 'USER'
    
    def can_manage_users(self):
        """Verifica si el usuario puede gestionar otros usuarios"""
        return self.user_level in ['ADMIN', 'MANAGER']
    
    def can_access_admin(self):
        """Verifica si el usuario puede acceder al panel de administración"""
        return self.user_level == 'ADMIN'


class UserProfile(models.Model):
    """
    Perfil extendido del usuario
    Información adicional que no está en el modelo User base
    """
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('Usuario')
    )
    
    bio = models.TextField(
        max_length=500, 
        blank=True,
        verbose_name=_('Biografía'),
        help_text=_('Descripción personal del usuario')
    )
    
    location = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('Ubicación')
    )
    
    website = models.URLField(
        blank=True,
        verbose_name=_('Sitio web')
    )
    
    birth_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_('Fecha de nacimiento')
    )
    
    # Configuraciones de privacidad
    privacy_email = models.BooleanField(
        default=False,
        verbose_name=_('Email público'),
        help_text=_('Permite que otros usuarios vean el email')
    )
    
    privacy_phone = models.BooleanField(
        default=False,
        verbose_name=_('Teléfono público'),
        help_text=_('Permite que otros usuarios vean el teléfono')
    )
    
    # Configuraciones de notificaciones
    notifications_email = models.BooleanField(
        default=True,
        verbose_name=_('Notificaciones por email')
    )
    
    notifications_push = models.BooleanField(
        default=True,
        verbose_name=_('Notificaciones push')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Perfil de usuario')
        verbose_name_plural = _('Perfiles de usuarios')
        
    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"
