import requests
from celery.utils.log import get_task_logger

from app.tasks.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="app.tasks.tasks.check_events_status")
def check_events_status():
    """
    Periodically check for events where end_time < now, and
    mark them as 'completed' if they're not already.
    """
    try:
        response = requests.get(
            "http://event_management_app:8100/api/internal/event-checker"
        )
        if response.status_code != 200:
            logger.error(
                f"Failed to check events status: {response.status_code} - {response.text}"
            )
        else:
            logger.info("Event checker task completed successfully!")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
