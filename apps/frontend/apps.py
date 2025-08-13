"""
Configuración de la aplicación frontend
"""

from django.apps import AppConfig


class FrontendConfig(AppConfig):
    """
    Configuración de la app frontend
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.frontend'
    verbose_name = 'Frontend'
