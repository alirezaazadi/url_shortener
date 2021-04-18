import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'url_shortener.settings')

celery_app = Celery('url_shortener')

celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.conf.task_default_queue = 'default'
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    'build_reports': {
        'task': 'app_shortener.tasks.daily_building_reports',
        'schedule': crontab(minute=0, hour=0),
    },
    'continuous_building_reports': {
        'task': 'app_shortener.tasks.continuous_building_reports',
        'schedule': crontab(hour='*/1'),
    }
}

"""
celery -A url_shortener worker -B  -l info
"""
