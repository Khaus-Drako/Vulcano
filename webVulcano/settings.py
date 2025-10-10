"""
Configuración principal de Django para el proyecto Vulcano.
Plataforma de gestión y visualización de proyectos arquitectónicos.
"""

import os
from pathlib import Path
from decouple import config, Csv
import dj_database_url

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: Mantener la clave secreta en producción
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-vulcano-2025')

# SECURITY WARNING: No ejecutar con debug=True en producción
DEBUG = config('DEBUG', default=False, cast=bool)

# Hosts permitidos - soporte para Railway
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# CSRF trusted origins para Railway
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8000',
    cast=Csv()
)

# Definición de aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Cloudinary - DEBE IR ANTES de las apps locales
    'cloudinary_storage',
    'cloudinary',
    
    # Apps locales
    'vulcano',
    
    # Apps de terceros
    'django_cleanup.apps.CleanupConfig',  # Limpieza automática de archivos huérfanos
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Servir archivos estáticos eficientemente
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'vulcano.middleware.TestModeMiddleware',  # Agrega test_mode a las peticiones
]

ROOT_URLCONF = 'webVulcano.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'vulcano' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'webVulcano.wsgi.application'

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS - Compatible con Railway PostgreSQL
# ============================================================================
DATABASES = {
    'default': dj_database_url.config(
        default=config(
            'DATABASE_URL',
            default=f"postgresql://{config('DB_USER', default='vulcano')}:"
                    f"{config('DB_PASS', default='0p3r4c10n3s')}@"
                    f"{config('DB_HOST', default='localhost')}:"
                    f"{config('DB_PORT', default='5432')}/"
                    f"{config('DB_NAME', default='vulcano')}"
        ),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Validación de contraseñas
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

# Internacionalización
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# ============================================================================
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS - WhiteNoise
# ============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'vulcano' / 'static',
]

# Configuración de WhiteNoise para servir archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================================
# CONFIGURACIÓN DE CLOUDINARY PARA ARCHIVOS MULTIMEDIA
# ============================================================================
CLOUDINARY_URL = config('CLOUDINARY_URL', default='')

if CLOUDINARY_URL:
    # Usar Cloudinary en producción
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    # Configuración de Cloudinary
    cloudinary.config(
        cloudinary_url=CLOUDINARY_URL
    )
    
    # Storage backend para archivos media
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    MEDIA_URL = '/media/'
    
else:
    # Fallback para desarrollo local
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Tipo de campo de clave primaria predeterminado
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de autenticación
LOGIN_URL = 'vulcano:login'
LOGIN_REDIRECT_URL = 'vulcano:dashboard'
LOGOUT_REDIRECT_URL = 'vulcano:home'

# Configuración de sesiones
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = True

# Configuración de mensajes
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================
# En producción (Railway), los logs se manejan por stdout/stderr
if DEBUG:
    # Crear directorio de logs solo en desarrollo
    os.makedirs(BASE_DIR / 'logs', exist_ok=True)
    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {asctime} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': BASE_DIR / 'logs' / 'vulcano.log',
                'maxBytes': 1024 * 1024 * 10,  # 10 MB
                'backupCount': 5,
                'formatter': 'verbose',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': BASE_DIR / 'logs' / 'vulcano_errors.log',
                'maxBytes': 1024 * 1024 * 10,  # 10 MB
                'backupCount': 5,
                'formatter': 'verbose',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'root': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'vulcano': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }
else:
    # En producción, logs simplificados a consola
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '{levelname} {asctime} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
            'vulcano': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }

# Configuración de caché
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'vulcano-cache',
        'TIMEOUT': 300,  # 5 minutos
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD PARA PRODUCCIÓN
# ============================================================================
if not DEBUG:
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # SSL/HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Prevención de XSS y otros ataques
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Ajustes de cookies
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_SAMESITE = 'Strict'

# Configuración de subida de archivos
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB

# ============================================================================
# CONFIGURACIÓN DE EMAIL
# ============================================================================
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'  # Console en desarrollo
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@vulcano.com')