import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Lên lịch task (ví dụ)
app.conf.beat_schedule = {
    'sync-wazuh-alerts': {
        'task': 'apps.wazuh_integration.tasks.sync_wazuh_alerts',
        'schedule': crontab(minute='*/5'),
    },
    'cleanup-old-logs': {
        'task': 'apps.activity_log.tasks.cleanup_old_logs',
        'schedule': crontab(hour=2, minute=0),
    },
}