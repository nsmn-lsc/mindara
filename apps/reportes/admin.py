from django.contrib import admin
from .models import ReporteGenerado


@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 
        'tipo', 
        'formato', 
        'generado_por', 
        'fecha_generacion', 
        'total_eventos',
        'incluir_detalles'
    ]
    list_filter = [
        'tipo', 
        'formato', 
        'fecha_generacion', 
        'incluir_detalles',
        'generado_por'
    ]
    search_fields = [
        'titulo', 
        'generado_por__username', 
        'generado_por__first_name',
        'generado_por__last_name'
    ]
    readonly_fields = [
        'fecha_generacion', 
        'nombre_archivo'
    ]
    date_hierarchy = 'fecha_generacion'
    
    fieldsets = (
        ('Información del Reporte', {
            'fields': ('titulo', 'tipo', 'formato')
        }),
        ('Generación', {
            'fields': ('generado_por', 'fecha_generacion', 'total_eventos')
        }),
        ('Opciones', {
            'fields': ('incluir_detalles',)
        }),
        ('Archivo', {
            'fields': ('nombre_archivo',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('generado_por')
    
    def has_add_permission(self, request):
        # Los reportes solo se generan desde las vistas, no desde el admin
        return False
