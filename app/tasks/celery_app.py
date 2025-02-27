from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "celery_worker",
    broker="redis://event_management_redis:6379/0",
    backend="redis://event_management_redis:6379/0",
)


celery_app.conf.update(
    result_expires=3600,
    worker_prefetch_multiplier=1,
    task_track_started=True,
)

celery_app.conf.beat_schedule = {
    "update_appointments_every_minute": {
        "task": "app.tasks.tasks.check_events_status",
        "schedule": crontab(minute="*/1"),
    },
}

celery_app.conf.broker_connection_retry_on_startup = True

celery_app.conf.imports = ["app.tasks.tasks"]
