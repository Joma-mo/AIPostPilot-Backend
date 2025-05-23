import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aipostpilot.settings')

app = Celery('aipostpilot')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-due-posts-every-minute': {
        'task': 'posts.tasks.publish_due_posts',
        'schedule': crontab(minute='*'),
    },
}
