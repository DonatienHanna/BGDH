import os
from celery import Celery

# Définir la variable d'environnement Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_signals_platform.settings')

app = Celery('trading_signals_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()