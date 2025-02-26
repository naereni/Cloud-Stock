from __future__ import absolute_import, unicode_literals

import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Cloud_Stock.settings")
app = Celery("Cloud_Stock")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_url = "redis://localhost:6379/0"
app.conf.broker_connection_retry_on_startup = True

app.conf.worker_log_datefmt = "%d.%m.%y %H:%M:%S"
app.conf.worker_log_format = "[%(asctime)s] - %(levelname)s - %(message)s"
app.conf.worker_task_log_format = "[%(asctime)s] - %(levelname)s - %(task_name)s: %(message)s"
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "ozon": {
        "task": "api.tasks.process_ozon",
        "schedule": timedelta(seconds=10),
    },
    "ymarket": {
        "task": "api.tasks.process_ymarket",
        "schedule": timedelta(seconds=10),
    },
    "wb": {
        "task": "api.tasks.process_wb",
        "schedule": timedelta(seconds=10),
    },
    "push-stocks": {
        "task": "api.tasks.pushing_stocks",
        "schedule": timedelta(seconds=10),
    },
}
