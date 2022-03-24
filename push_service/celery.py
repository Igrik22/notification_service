import os
from celery import Celery
from celery.schedules import crontab
# setting the Django settings module.

# set the default Django settings module for the 'celery' program.
# this is also used in manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'push_service.settings')
# Get the base REDIS URL, default to redis' default
BASE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

app = Celery('push_service')
# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'send_our_distribution': {
        'task': 'core.tasks.send_complete_distribution',
        'schedule': 5.0,
        'args': (),
    },
}

# Looks up for task modules in Django applications and loads them
app.autodiscover_tasks()
