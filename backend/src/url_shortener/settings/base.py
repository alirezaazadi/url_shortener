from datetime import timedelta
from pathlib import Path

import environ

env = environ.Env(DEBUG=False)

environ.Env.read_env()

MODE = env('MODE', default='development')

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env('SECRET_KEY', default='django-insecure-qku$(n0rs!aj79h#3(eofq8^q8($t@pum+4m&%#33re*ftd4mk')

DEBUG = MODE == 'development'

ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='*').split(',')

APPEND_SLASH = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # project apps

    'app_users',
    'app_shortener',

    # third party apps

    'rest_framework',
    'django_user_agents',
    'cacheops',
    'django_pickling',
    'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'url_shortener.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': []
        ,
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

WSGI_APPLICATION = 'url_shortener.wsgi.application'

DATABASES = {
    'default': {
        **env.db(),
        'CONN_MAX_AGE': 500
    },
}

REDIS_URL = env("REDIS_URL", default='redis://localhost:6379')

CACHES = {
    'default':
        {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f'{REDIS_URL}',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'TIMEOUT': 60 * 60 * 24
            },
        }
}

CACHEOPS_REDIS = f"{REDIS_URL}/1"

CACHEOPS_DEFAULTS = {
    'timeout': 60 * 60
}

CACHEOPS = {
    '*.*': {'ops': (), 'timeout': 60 * 60 * 60},
}

CACHEOPS_LRU = True

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=env.int('ACCESS_TOKEN_LIFETIME', default=60 * 60 * 2)),
    'REFRESH_TOKEN_LIFETIME': timedelta(seconds=env.int('REFRESH_TOKEN_LIFETIME', default=60 * 60 * 72)),
    'ROTATE_REFRESH_TOKENS': True,
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'app_users.User'

CELERY_BROKER_URL = env.str('CELERY_BROKER_URL', f'{REDIS_URL}/2')
CELERY_ACCEPT_CONTENT = ['application/json', 'pickle']
CELERY_IGNORE_RESULT = True
CELERY_TASK_SERIALIZER = 'pickle'
USER_AGENTS_CACHE = 'default'
