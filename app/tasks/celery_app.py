from celery import Celery

# Create the Celery application
celery_app = Celery(
    "celery_worker",
    broker="redis://event_management_redis:6379/0",
    backend="redis://event_management_redis:6379/0",
)

# Optional: Add any Celery configuration settings here
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
