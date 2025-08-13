"""
URLs para la aplicación de eventos
"""

from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    # Vistas principales
    path('', views.EventosView.as_view(), name='eventos'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
    path('notificaciones/', views.notificaciones_usuario, name='notificaciones'),
    
    # APIs
    path('api/mis-eventos/', views.api_eventos_usuario, name='api_eventos_usuario'),
    path('api/perfil-stats/', views.api_perfil_stats, name='api_perfil_stats'),
    
    # APIs nuevas para el frontend
    path('api/eventos/', views.api_eventos, name='api_eventos'),
    path('api/eventos/<int:evento_id>/', views.api_evento_detail, name='api_evento_detail'),
    path('api/categorias/', views.api_categorias, name='api_categorias'),
]
