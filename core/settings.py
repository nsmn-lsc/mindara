"""
Django settings for Mindara project.
"""

from pathlib import Path
from decouple import config, Csv
import mimetypes
import os
from urllib.parse import urlparse

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    
    # Local apps
    'apps.authentication',
    'apps.frontend',
    'apps.eventos',
    'apps.notificaciones',
    'apps.reportes',
]

# Ajustes de tipos MIME en algunos entornos minimalistas (Render) donde .css/.js pueden resolverse a text/plain
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Recomendado primero
    'whitenoise.middleware.WhiteNoiseMiddleware',     # Justo después de Security
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Middleware personalizado para expirar sesión tras inactividad
    'core.middleware.IdleSessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}

# Soporte DATABASE_URL (Render u otros)
DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(DATABASE_URL, conn_max_age=600)

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Mexico_City'  # Zona horaria de México
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
# Incluir carpeta 'static' solo si existe (evita W004 en producción si faltó en el repo)
_static_dir = BASE_DIR / 'static'
if _static_dir.exists():
    STATICFILES_DIRS = [_static_dir]
else:
    STATICFILES_DIRS = []
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise: servir archivos estáticos comprimidos y con hash en producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 365  # 1 año
# Permitir servir sin problemas en hosting que hace requests con diferentes origins (opcional)
WHITENOISE_ALLOW_ALL_ORIGINS = True

# En caso de que surjan errores de manifest en producción (archivos faltantes), podemos forzar fallback a la versión simple:
if os.environ.get('DISABLE_MANIFEST_STATIC', '0') == '1':
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Forzar almacenamiento simple (sin compresión ni manifest) para depuración de 404
if os.environ.get('FORCE_SIMPLE_STATIC', '0') == '1':
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files (uploaded by users)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging para diagnosticar 404 de estáticos en producción
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'whitenoise': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

# ==========================
# Configuración de Sesiones
# ==========================
# Duración máxima absoluta de la cookie de sesión (8h por defecto)
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=8 * 60 * 60, cast=int)
# Forzar expiración al cerrar el navegador (mitiga acceso desde equipos compartidos)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Guardar la sesión en cada request para renovar expiración (sliding window)
SESSION_SAVE_EVERY_REQUEST = True
# Timeout de inactividad (segundos) para cierre proactivo (30 min por defecto)
IDLE_SESSION_TIMEOUT = config('IDLE_SESSION_TIMEOUT', default=30 * 60, cast=int)
# Nombre clave en sesión para tracking de actividad
IDLE_SESSION_KEY = '_last_activity_ts'

# Authentication settings
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Ajustes de seguridad producción
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    X_FRAME_OPTIONS = 'DENY'
    REFERRER_POLICY = 'same-origin'


# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
}

# CORS Configuration - Para React frontend
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Vite alternative port
]

CORS_ALLOW_CREDENTIALS = True

# CORS headers permitidos
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
