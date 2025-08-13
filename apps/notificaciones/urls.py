"""
URLs para el módulo de notificaciones
"""

from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    # Gestión de notificaciones (admin/manager)
    path('', views.NotificacionListView.as_view(), name='lista'),
    path('crear/', views.NotificacionCreateView.as_view(), name='crear'),
    path('crear-rapida/', views.NotificacionRapidaCreateView.as_view(), name='crear_rapida'),
    path('editar/<int:pk>/', views.NotificacionUpdateView.as_view(), name='editar'),
    path('eliminar/<int:pk>/', views.NotificacionDeleteView.as_view(), name='eliminar'),
    
    # Vista para usuarios
    path('mis-notificaciones/', views.mis_notificaciones, name='mis_notificaciones'),
    
    # APIs AJAX
    path('marcar-leida/', views.marcar_como_leida, name='marcar_como_leida'),
    path('marcar-todas-leidas/', views.marcar_todas_como_leidas, name='marcar_todas_como_leidas'),
    path('api/no-leidas/', views.obtener_notificaciones_no_leidas, name='obtener_no_leidas'),
    path('toggle-estado/<int:notificacion_id>/', views.toggle_notificacion_estado, name='toggle_estado'),
]
