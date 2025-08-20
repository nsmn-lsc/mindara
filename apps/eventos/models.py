"""
Modelos para la aplicación de eventos
Sistema de gestión de eventos para usuarios de Mindara
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.authentication.models import User


class CategoriaEvento(models.Model):
    """
    Categorías para clasificar los eventos
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Nombre de la categoría'),
        help_text=_('Nombre único para la categoría del evento')
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name=_('Descripción'),
        help_text=_('Descripción detallada de la categoría')
    )
    
    color = models.CharField(
        max_length=7,
        default='#06A77D',
        verbose_name=_('Color'),
        help_text=_('Color en formato hexadecimal para identificar la categoría')
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name=_('Activa'),
        help_text=_('Si la categoría está disponible para usar')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Fecha de creación')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )
    
    class Meta:
        verbose_name = _('Categoría de Evento')
        verbose_name_plural = _('Categorías de Eventos')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Evento(models.Model):
    """
    Modelo principal para los eventos del sistema
    Adaptado a los requerimientos específicos de Mindara
    """
    
    # Etapas del evento (antes "estado")
    ETAPA_CHOICES = [
        ('planificacion', _('Planificación')),
        ('revision', _('Revisión')),
        ('confirmado', _('Confirmado')),
        ('cancelado', _('Cancelado')),
        ('pospuesto', _('Pospuesto')),
    ]
    
    # Prioridades del evento
    PRIORIDAD_CHOICES = [
        ('baja', _('Baja')),
        ('media', _('Media')),
        ('alta', _('Alta')),
        ('urgente', _('Urgente')),
    ]
    
    # Duración en horas (opciones comunes)
    DURACION_CHOICES = [
        ('0.5', _('30 minutos')),
        ('1', _('1 hora')),
        ('1.5', _('1.5 horas')),
        ('2', _('2 horas')),
        ('3', _('3 horas')),
        ('4', _('4 horas')),
        ('6', _('6 horas')),
        ('8', _('8 horas (día completo)')),
        ('otro', _('Otra duración')),
    ]
    
    # Información básica
    nombre_evento = models.CharField(
        max_length=200,
        default='Evento sin nombre',
        verbose_name=_('Nombre del evento'),
        help_text=_('Nombre descriptivo del evento')
    )
    
    objetivo = models.TextField(
        default='Por definir',
        verbose_name=_('Objetivo'),
        help_text=_('Objetivo principal del evento')
    )
    
    # Fechas y horarios
    # Usar default dinámico; timezone.now devuelve datetime, Django toma la porción de fecha
    from django.utils import timezone as _tz  # import local to avoid circular issues at import time
    fecha_evento = models.DateField(
        default=_tz.now,
        verbose_name=_('Fecha del evento'),
        help_text=_('Día en que se realizará el evento')
    )
    
    hora_evento = models.TimeField(
        default='09:00',
        verbose_name=_('Hora del evento'),
        help_text=_('Hora de inicio del evento')
    )
    
    duracion = models.CharField(
        max_length=10,
        choices=DURACION_CHOICES,
        default='2',
        verbose_name=_('Duración'),
        help_text=_('Duración estimada del evento')
    )
    
    duracion_personalizada = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.25)],
        verbose_name=_('Duración personalizada (horas)'),
        help_text=_('Solo si seleccionaste "Otra duración"')
    )
    
    # Ubicación y logística
    sede = models.CharField(
        max_length=300,
        default='Por definir',
        verbose_name=_('Sede'),
        help_text=_('Lugar donde se realizará el evento')
    )
    
    link_maps = models.URLField(
        blank=True,
        verbose_name=_('Link de Google Maps'),
        help_text=_('Enlace a Google Maps de la ubicación')
    )
    
    aforo = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        verbose_name=_('Aforo'),
        help_text=_('Número máximo de participantes')
    )
    
    participantes = models.TextField(
        blank=True,
        verbose_name=_('Participantes'),
        help_text=_('Lista de participantes esperados (uno por línea o separados por comas)')
    )
    
    # Usuario responsable
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='eventos_responsable',
        verbose_name=_('Usuario responsable'),
        help_text=_('Usuario responsable del evento')
    )
    
    # Gestión del evento
    etapa = models.CharField(
        max_length=20,
        choices=ETAPA_CHOICES,
        default='planificacion',
        verbose_name=_('Etapa'),
        help_text=_('Etapa actual del evento')
    )
    
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='media',
        verbose_name=_('Prioridad'),
        help_text=_('Nivel de prioridad del evento')
    )
    
    # Carpeta ejecutiva (PowerPoint)
    carpeta_ejecutiva = models.BooleanField(
        default=False,
        verbose_name=_('¿Tiene carpeta ejecutiva?'),
        help_text=_('Indica si el evento incluye una presentación PowerPoint')
    )
    
    carpeta_ejecutiva_liga = models.URLField(
        blank=True,
        verbose_name=_('Liga de carpeta ejecutiva'),
        help_text=_('Enlace a la presentación en Google Drive, OneDrive, etc.')
    )

    # Evidencias del evento (enlace a carpeta/archivo en la nube)
    evidencias = models.URLField(
        blank=True,
        verbose_name=_('Liga de evidencias'),
        help_text=_('Enlace a carpeta/archivo en la nube (Drive, OneDrive, Dropbox, etc.)')
    )
    
    # Compromisos y seguimiento
    compromisos = models.TextField(
        blank=True,
        verbose_name=_('Compromisos'),
        help_text=_('Compromisos y acuerdos derivados del evento')
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name=_('Observaciones'),
        help_text=_('Notas adicionales y observaciones sobre el evento')
    )
    
    # Metadatos
    marca_temporal = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Marca temporal'),
        help_text=_('Fecha y hora de creación del registro')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Fecha de actualización')
    )
    
    class Meta:
        verbose_name = _('Evento')
        verbose_name_plural = _('Eventos')
        ordering = ['-fecha_evento', '-hora_evento']
        indexes = [
            models.Index(fields=['fecha_evento']),
            models.Index(fields=['usuario']),
            models.Index(fields=['etapa']),
            models.Index(fields=['prioridad']),
        ]
    
    def __str__(self):
        return f"{self.nombre_evento} - {self.fecha_evento.strftime('%d/%m/%Y')}"
    
    @property
    def duracion_real(self):
        """Devuelve la duración real en horas"""
        if self.duracion == 'otro':
            # Garantizar float aun cuando sea Decimal o None
            return float(self.duracion_personalizada or 0)
        return float(self.duracion)
    
    @property
    def fecha_hora_completa(self):
        """Combina fecha y hora para comparaciones"""
        from datetime import datetime
        from django.utils import timezone
        dt = datetime.combine(self.fecha_evento, self.hora_evento)
        # Asegurar datetime consciente de zona horaria
        if timezone.is_naive(dt):
            return timezone.make_aware(dt, timezone.get_current_timezone())
        return dt
    
    @property
    def esta_en_progreso(self):
        """Verifica si el evento está actualmente en progreso"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        inicio = self.fecha_hora_completa
        fin = inicio + timedelta(hours=self.duracion_real)
        
        return inicio <= now <= fin
    
    @property
    def ha_terminado(self):
        """Verifica si el evento ya terminó"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        fin = self.fecha_hora_completa + timedelta(hours=self.duracion_real)
        
        return fin < now
    
    @property
    def participantes_count(self):
        """Cuenta el número de participantes"""
        if not self.participantes:
            return 0
        # Contar por líneas o por comas
        participantes_list = self.participantes.replace(',', '\n').split('\n')
        return len([p.strip() for p in participantes_list if p.strip()])
    
    def puede_editar(self, user):
        """Verifica si un usuario puede editar este evento"""
        return (
            self.usuario == user or 
            user.user_level in ['ADMIN', 'MANAGER']
        )
    
    def puede_ver(self, user):
        """Verifica si un usuario puede ver este evento"""
        return (
            self.usuario == user or 
            user.user_level in ['ADMIN', 'MANAGER']
        )
    
    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        # Validar que la fecha no sea en el pasado (aplica para creación y edición)
        if self.fecha_evento < timezone.now().date():
            raise ValidationError('La fecha del evento no puede ser en el pasado')
        
        # Validar carpeta ejecutiva
        if self.carpeta_ejecutiva and not self.carpeta_ejecutiva_liga:
            raise ValidationError('Debe proporcionar la liga de la carpeta ejecutiva')
        
        # Validar duración personalizada
        if self.duracion == 'otro' and not self.duracion_personalizada:
            raise ValidationError('Debe especificar la duración personalizada')
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para validaciones adicionales"""
        self.full_clean()
        super().save(*args, **kwargs)


