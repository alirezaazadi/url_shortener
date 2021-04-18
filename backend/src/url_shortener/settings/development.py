from .base import *

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost'
]

INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

APPEND_SLASH = True
