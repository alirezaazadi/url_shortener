import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env()
MODE = env('MODE', default='development')

if MODE == 'development':
    from .development import *
elif MODE == 'production':
    from .production import *
