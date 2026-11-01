import os

from celery import Celery

#from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.configs.settings.dev')

app = Celery('app')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

