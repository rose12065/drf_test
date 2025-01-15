from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
from formhandling.tasks import send_reminder_email

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf.settings')

app = Celery('drf')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery Beat configuration for periodic tasks
# app.conf.beat_schedule = {
#     'send-daily-reminder': {
#         'task': 'formhandling.tasks.send_reminder_email',  # The task to execute
#         'schedule': crontab(minute='*'),  
#         'args': ('greenmart893@gmail.com', 'Daily Reminder', 'This is your daily reminder email!'),
#     },
# }

# Schedule the task to run after 10 minutes
send_reminder_email.apply_async(
    args=('greenmart893@gmail.com', 'Reminder Email for apply_async', 'This is a reminder.'),
    eta=datetime.utcnow() + timedelta(minutes=10)
)


app.conf.timezone = 'UTC'

app.conf.broker_connection_retry_on_startup = True


