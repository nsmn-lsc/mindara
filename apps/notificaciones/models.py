"""
Modelos para el sistema de notificaciones de Mindara
Permite a los administradores y managers enviar notificaciones a los usuarios
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone


class NotificacionManager(models.Manager):
    """Manager personalizado para notificaciones"""
    
    def get_for_user(self, usuario):
        """Obtiene todas las notificaciones para un usuario específico"""
        from django.db.models import Q
        
        # Notificaciones dirigidas específicamente al usuario
        # o a su nivel de usuario, o notificaciones generales
        return self.filter(
            Q(usuarios_objetivo=usuario) | 
            Q(nivel_usuario_objetivo=usuario.user_level) |
            Q(usuarios_objetivo__isnull=True, nivel_usuario_objetivo__isnull=True)
        ).filter(
            activa=True
        ).distinct()

    def activas(self):
        """Obtiene solo las notificaciones activas y no expiradas"""
        return self.filter(
            activa=True
        ).filter(
            models.Q(fecha_expiracion__isnull=True) |
            models.Q(fecha_expiracion__gt=timezone.now())
        )


class Notificacion(models.Model):
    """
    Modelo para las notificaciones del sistema
    """
    
    TIPOS_CHOICES = [
        ('general', 'General'),
        ('sistema', 'Sistema'),
        ('evento', 'Evento'),
        ('personal', 'Personal'),
    ]
    
    PRIORIDADES_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]
    
    NIVELES_USUARIO = [
        ('ADMIN', 'Administradores'),
        ('MANAGER', 'Managers'),
        ('USER', 'Usuarios'),
    ]
    
    # Información básica de la notificación
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título',
        help_text='Título de la notificación'
    )
    
    mensaje = models.TextField(
        verbose_name='Mensaje',
        help_text='Contenido de la notificación'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_CHOICES,
        default='general',
        verbose_name='Tipo de notificación'
    )
    
    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDADES_CHOICES,
        default='media',
        verbose_name='Prioridad'
    )
    
    # Información del creador
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notificaciones_creadas',
        verbose_name='Creado por'
    )
    
    # Targeting de destinatarios
    usuarios_objetivo = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='notificaciones_dirigidas',
        verbose_name='Usuarios objetivo',
        help_text='Usuarios específicos que recibirán la notificación'
    )
    
    nivel_usuario_objetivo = models.CharField(
        max_length=10,
        choices=NIVELES_USUARIO,
        blank=True,
        null=True,
        verbose_name='Nivel de usuario objetivo',
        help_text='Nivel de usuarios que recibirán la notificación'
    )
    
    # Configuración temporal
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    fecha_expiracion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de expiración',
        help_text='Fecha después de la cual la notificación no será visible'
    )
    
    # Estado
    activa = models.BooleanField(
        default=True,
        verbose_name='Activa',
        help_text='Si está activa, la notificación será visible para los usuarios'
    )
    
    # Manager personalizado
    objects = NotificacionManager()
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_display()}"
    
    @property
    def esta_expirada(self):
        """Verifica si la notificación ha expirado"""
        if self.fecha_expiracion:
            return timezone.now() > self.fecha_expiracion
        return False
    
    def puede_ver_usuario(self, usuario):
        """Verifica si un usuario puede ver esta notificación"""
        if not self.activa:
            return False
            
        if self.esta_expirada:
            return False
            
        # Verificar targeting específico
        if self.usuarios_objetivo.exists():
            return self.usuarios_objetivo.filter(id=usuario.id).exists()
        
        # Verificar targeting por nivel
        if self.nivel_usuario_objetivo:
            return self.nivel_usuario_objetivo == usuario.user_level
        
        # Si no hay targeting específico, es para todos
        return True

    def marcar_como_leida(self, usuario):
        """Marca esta notificación como leída por el usuario"""
        NotificacionLeida.objects.get_or_create(
            notificacion=self,
            usuario=usuario
        )

    def esta_leida_por(self, usuario):
        """Verifica si esta notificación ha sido leída por el usuario"""
        return self.lecturas.filter(usuario=usuario).exists()


class NotificacionLeida(models.Model):
    """
    Modelo para trackear qué usuarios han leído cada notificación
    """
    
    notificacion = models.ForeignKey(
        Notificacion,
        on_delete=models.CASCADE,
        related_name='lecturas',
        verbose_name='Notificación'
    )
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones_leidas',
        verbose_name='Usuario'
    )
    
    fecha_lectura = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de lectura'
    )
    
    class Meta:
        verbose_name = 'Notificación leída'
        verbose_name_plural = 'Notificaciones leídas'
        unique_together = ['notificacion', 'usuario']
        ordering = ['-fecha_lectura']
        
    def __str__(self):
        return f"{self.usuario.username} leyó: {self.notificacion.titulo}"
