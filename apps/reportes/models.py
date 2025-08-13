"""
Modelos para la aplicación de reportes
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class ReporteGenerado(models.Model):
    """
    Modelo para trackear los reportes generados
    """
    
    TIPOS_REPORTE = [
        ('agenda', 'Eventos en Agenda'),
        ('semana', 'Eventos de la Semana'),
        ('mes', 'Eventos del Mes'),
        ('carpeta_ejecutiva', 'Eventos con Carpeta Ejecutiva'),
        ('personalizado', 'Reporte Personalizado'),
    ]
    
    FORMATOS = [
        ('xlsx', 'Excel (XLSX)'),
        ('pdf', 'PDF'),
    ]
    
    # Información básica del reporte
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_REPORTE,
        verbose_name='Tipo de Reporte'
    )
    
    formato = models.CharField(
        max_length=10,
        choices=FORMATOS,
        verbose_name='Formato'
    )
    
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título del Reporte'
    )
    
    # Usuario que generó el reporte
    generado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reportes_generados',
        verbose_name='Generado por'
    )
    
    # Fechas del reporte
    fecha_generacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Generación'
    )
    
    fecha_inicio_filtro = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Inicio (Filtro)'
    )
    
    fecha_fin_filtro = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Fin (Filtro)'
    )
    
    # Configuración del reporte
    incluir_detalles = models.BooleanField(
        default=True,
        verbose_name='Incluir Detalles'
    )
    
    solo_confirmados = models.BooleanField(
        default=False,
        verbose_name='Solo Eventos Confirmados'
    )
    
    # Metadatos
    total_eventos = models.IntegerField(
        default=0,
        verbose_name='Total de Eventos'
    )
    
    archivo_generado = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Ruta del Archivo'
    )
    
    class Meta:
        verbose_name = 'Reporte Generado'
        verbose_name_plural = 'Reportes Generados'
        ordering = ['-fecha_generacion']
        
    def __str__(self):
        return f"{self.titulo} - {self.get_formato_display()} ({self.fecha_generacion.strftime('%d/%m/%Y %H:%M')})"
    
    @property
    def nombre_archivo(self):
        """Genera el nombre del archivo basado en el tipo y fecha"""
        fecha_str = self.fecha_generacion.strftime('%Y%m%d_%H%M%S')
        return f"{self.tipo}_{fecha_str}.{self.formato}"
