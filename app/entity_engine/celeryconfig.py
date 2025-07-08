import os
from celery.schedules import crontab

beat_schedule = {
    "run-every-3-days": {
        "task": "tasks.process_data",
        "schedule": crontab(day_of_month="*/3"),  # Every 3 days
    },
}

broker_url = os.getenv("RABBITMQ_URL")
beat_schedule = beat_schedule
