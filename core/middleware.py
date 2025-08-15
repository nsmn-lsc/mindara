import time
from django.conf import settings
from django.contrib import auth
from django.utils.deprecation import MiddlewareMixin

class IdleSessionMiddleware(MiddlewareMixin):
    """Cierra la sesión si el usuario supera el periodo de inactividad definido.

    Reglas:
    - Usa settings.IDLE_SESSION_TIMEOUT (segundos) como umbral.
    - Guarda timestamp de última actividad en request.session[settings.IDLE_SESSION_KEY].
    - Renueva timestamp en cada request autenticada.
    - Si excede el umbral, hace logout y limpia la sesión.
    """
    def process_request(self, request):
        if not request.user.is_authenticated:
            return
        timeout = getattr(settings, 'IDLE_SESSION_TIMEOUT', 1800)
        key = getattr(settings, 'IDLE_SESSION_KEY', '_last_activity_ts')
        now = int(time.time())
        last = request.session.get(key, now)
        if last + timeout < now:
            auth.logout(request)
            # Limpia la sesión para evitar reutilización
            request.session.flush()
            return
        request.session[key] = now
