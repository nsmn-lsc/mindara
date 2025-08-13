"""
URLs para la aplicación de reportes
"""

from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.ReportesView.as_view(), name='index'),
    path('agenda/', views.generar_reporte_agenda, name='agenda'),
    path('semana/', views.generar_reporte_semana, name='semana'),
    path('mes/', views.generar_reporte_mes, name='mes'),
    path('carpeta-ejecutiva/', views.generar_reporte_carpeta_ejecutiva, name='carpeta_ejecutiva'),
    path('historial/', views.historial_reportes, name='historial'),
]
