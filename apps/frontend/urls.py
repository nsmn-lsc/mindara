"""
URLs del frontend
Sistema de autenticación sin registro público
"""

from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    # Vistas principales
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/eventos-usuarios/', views.EventosUsuariosStatsView.as_view(), name='eventos_usuarios_stats'),
    path('logout/', views.logout_view, name='logout'),
    path('ayuda/', views.AyudaView.as_view(), name='ayuda'),
    
    # Gestión de usuarios (solo administradores)
    path('admin/users/', views.UserManagementView.as_view(), name='user_management'),
    path('admin/users/create/', views.CreateUserView.as_view(), name='create_user'),
    path('admin/users/<int:user_id>/edit/', views.EditUserView.as_view(), name='edit_user'),
    
    # APIs AJAX
    path('login-api/', views.login_api, name='login_api'),
    path('api/profile/', views.user_profile_api, name='user_profile_api'),
    path('api/dashboard-stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('api/users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('api/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
]
