"""
Django settings for Bus project.
Compatible : développement local (SQLite) + production (PostgreSQL sur Render)
"""
from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# ============================================
# CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
# ============================================
# Charge le fichier .env s'il existe (en local uniquement)
# Sur Render, les variables sont injectées par la plateforme
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================
# SÉCURITÉ
# ============================================
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError(
        "❌ SECRET_KEY manquante. "
        "Crée un fichier .env à la racine avec SECRET_KEY=... "
        "ou configure la variable d'environnement sur Render."
    )

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    h.strip() for h in os.getenv(
        'ALLOWED_HOSTS',
        'localhost,127.0.0.1,0.0.0.0'
    ).split(',') if h.strip()
]

# Render fournit automatiquement le domaine externe
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# ============================================
# APPLICATIONS
# ============================================
INSTALLED_APPS = [
    # ASGI / Channels EN PREMIER (obligatoire)
    'daphne',
    'channels',

    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tiers
    'corsheaders',
    'rest_framework',

    # Vos apps
    'user',
    'bus_tracking',
    'payements',
]

AUTH_USER_MODEL = "user.User"

# Redirections auth
LOGIN_URL = "user:login"
LOGIN_REDIRECT_URL = "user:dashboard"
LOGOUT_REDIRECT_URL = "user:login"


# ============================================
# MIDDLEWARE
# ============================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # Sert les static en prod
    'corsheaders.middleware.CorsMiddleware',        # AVANT CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================
# CORS / CSRF
# ============================================
CORS_ALLOW_ALL_ORIGINS = DEBUG   # ouvert en dev, fermé en prod

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv(
        'CSRF_TRUSTED_ORIGINS',
        'http://localhost:8000,http://127.0.0.1:8000'
    ).split(',') if o.strip()
]

# Render ajoute automatiquement le domaine HTTPS
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')


# ============================================
# URLS / TEMPLATES / WSGI-ASGI
# ============================================
ROOT_URLCONF = 'Bus.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Bus.wsgi.application'
ASGI_APPLICATION = 'Bus.asgi.application'   # Pour Channels


# ============================================
# BASE DE DONNÉES
# ============================================
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Production : PostgreSQL managé (Render)
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Développement : SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ============================================
# AUTHENTIFICATION
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================
# INTERNATIONALISATION
# ============================================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Niamey'
USE_I18N = True
USE_TZ = True


# ============================================
# FICHIERS STATIQUES
# ============================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise : compression + cache des static en prod
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ============================================
# REDIS + CHANNELS (WebSockets)
# ============================================
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [REDIS_URL],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}


# ============================================
# EMAIL
# ============================================
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)


# ============================================
# SÉCURITÉ PRODUCTION (activée si DEBUG=False)
# ============================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'