"""
Vistas principales del proyecto Mindara
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.authentication.models import User


class HomeView(TemplateView):
    """
    Vista principal de la aplicación
    Servirá como punto de entrada para React
    """
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Mindara - Sistema de Autenticación',
            'description': 'Sistema de autenticación con 3 niveles de usuario',
            'api_base_url': '/api/auth/',
        })
        return context


@api_view(['GET'])
@permission_classes([AllowAny])
def api_status(request):
    """
    Endpoint para verificar el estado de la API
    """
    return Response({
        'status': 'active',
        'message': 'API Mindara funcionando correctamente',
        'version': '1.0.0',
        'endpoints': {
            'authentication': '/api/auth/',
            'admin': '/admin/',
            'api_browser': '/api-auth/',
        },
        'user_levels': [
            {'level': 'ADMIN', 'description': 'Administrador - Acceso completo'},
            {'level': 'MANAGER', 'description': 'Gestor - Gestión limitada'},
            {'level': 'USER', 'description': 'Usuario - Acceso básico'},
        ]
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """
    Información general de la API para desarrolladores
    """
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
    }
    
    return Response({
        'project': 'Mindara Authentication System',
        'description': 'Sistema de autenticación con Django REST Framework y React',
        'features': [
            'Autenticación JWT',
            '3 niveles de usuario (ADMIN, MANAGER, USER)',
            'API REST completa',
            'Permisos granulares',
            'Panel de administración personalizado'
        ],
        'technology_stack': {
            'backend': 'Django 5.2.5 + Django REST Framework',
            'frontend': 'React (próximamente)',
            'database': 'PostgreSQL',
            'authentication': 'JWT (Simple JWT)'
        },
        'statistics': stats,
        'documentation': {
            'api_endpoints': '/api/auth/',
            'admin_panel': '/admin/',
            'browsable_api': '/api-auth/'
        }
    })
