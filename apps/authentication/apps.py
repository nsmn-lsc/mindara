"""
Configuración de la aplicación de autenticación
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuración de la app authentication
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = 'Autenticación'
    
    def ready(self):
        """
        Código que se ejecuta cuando la app está lista
        Aquí se pueden importar signals, etc.
        """
        # Importar signals si los necesitamos en el futuro
        # import apps.authentication.signals
        pass
