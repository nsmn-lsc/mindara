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
        # Verificaciones defensivas: puede ejecutarse antes de que auth procese user en algunos edge cases
        user = getattr(request, 'user', None)
        session = getattr(request, 'session', None)
        if user is None or session is None or not getattr(user, 'is_authenticated', False):
            return
        timeout = getattr(settings, 'IDLE_SESSION_TIMEOUT', 1800)
        if timeout <= 0:
            return
        key = getattr(settings, 'IDLE_SESSION_KEY', '_last_activity_ts')
        now = int(time.time())
        last = session.get(key, now)
        if last + timeout < now:
            auth.logout(request)
            try:
                session.flush()
            except Exception:
                pass
            return
        session[key] = now
