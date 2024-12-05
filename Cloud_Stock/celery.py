from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Cloud_Stock.settings")
app = Celery("Cloud_Stock")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_url = "redis://localhost:6379/0"
app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "poll-orders": {
        "task": "api.tasks.polling_orders",
        "schedule": timedelta(seconds=10),
    },
    "poll-reserved": {
        "task": "api.tasks.polling_reserved",
        "schedule": timedelta(seconds=10),
    },
    # "update-stocks": {
    #     "task": "api.tasks.update_stocks",
    #     "schedule": timedelta(seconds=120),
    # },
    "poll-returned": {
        "task": "api.tasks.polling_returned",
        "schedule": timedelta(seconds=10),
    },
}
