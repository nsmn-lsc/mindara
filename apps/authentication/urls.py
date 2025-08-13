"""
URLs para la API de autenticación
Endpoints REST para el frontend React
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    UserProfileView,
    PasswordChangeView,
    UserListView,
    UserDetailView,
    UserLevelUpdateView,
    logout_view,
    user_stats_view,
)

app_name = 'authentication'

# URLs de la API REST
urlpatterns = [
    # ========== AUTENTICACIÓN ==========
    # POST /api/auth/login/ - Iniciar sesión y obtener tokens JWT
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    
    # POST /api/auth/register/ - Registrar nuevo usuario
    path('register/', UserRegistrationView.as_view(), name='register'),
    
    # POST /api/auth/logout/ - Cerrar sesión
    path('logout/', logout_view, name='logout'),
    
    # POST /api/auth/refresh/ - Renovar token de acceso
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ========== PERFIL DE USUARIO ==========
    # GET/PUT /api/auth/profile/ - Obtener/actualizar perfil del usuario autenticado
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # POST /api/auth/change-password/ - Cambiar contraseña
    path('change-password/', PasswordChangeView.as_view(), name='change_password'),
    
    # ========== GESTIÓN DE USUARIOS ==========
    # GET /api/auth/users/ - Listar usuarios (según permisos)
    path('users/', UserListView.as_view(), name='user_list'),
    
    # GET/PUT/DELETE /api/auth/users/{id}/ - Detalle de usuario específico
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    
    # PATCH /api/auth/users/{id}/level/ - Cambiar nivel de usuario (solo admins)
    path('users/<int:pk>/level/', UserLevelUpdateView.as_view(), name='user_level_update'),
    
    # ========== ESTADÍSTICAS ==========
    # GET /api/auth/stats/ - Estadísticas de usuarios (solo admins)
    path('stats/', user_stats_view, name='user_stats'),
]
