# resume_analyzer/celery.py
from celery import Celery
import os
from mongoengine import connect

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_analyzer.settings')

# Create the Celery application
app = Celery('resume_analyzer')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

connect(
    db='resume_analysis',
    host='localhost',
    port=27017,
    alias='default'
)
print("Celery connected to MongoDB: resume_data")
