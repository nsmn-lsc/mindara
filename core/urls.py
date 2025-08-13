"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

"""
URL configuration for Mindara project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import api_status, api_info
from django.http import JsonResponse
from django.db import connection
from django.utils.timezone import now

def healthz(_request):
    db_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except Exception:
        db_ok = False
    status_code = 200 if db_ok else 500
    return JsonResponse({
        'ok': db_ok,
        'db': 'ok' if db_ok else 'down',
        'time': now().isoformat(),
        'app': 'mindara'
    }, status=status_code)

urlpatterns = [
    # Frontend (login, dashboard, etc.)
    path('', include('apps.frontend.urls')),
    
    # Módulo de eventos
    path('eventos/', include('apps.eventos.urls')),
    
    # Módulo de notificaciones
    path('notificaciones/', include('apps.notificaciones.urls')),
    
    # Módulo de reportes
    path('reportes/', include('apps.reportes.urls')),
    
    # Panel de administración Django
    path("admin/", admin.site.urls),
    
    # API REST para autenticación
    path('api/auth/', include('apps.authentication.urls')),
    
    # Endpoints de información de la API
    path('api/status/', api_status, name='api_status'),
    path('api/info/', api_info, name='api_info'),
    path('healthz/', healthz, name='healthz'),
    
    # API REST Framework browsable API (solo en desarrollo)
    path('api-auth/', include('rest_framework.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
