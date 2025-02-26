from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import config
from app.models.event import Event, EventStatus
from app.tasks.celery_app import celery_app

# Create a synchronous SQLAlchemy engine / session factory
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def check_events_status():
    """
    Periodically check for events where end_time < now, and
    mark them as 'completed' if they're not already.
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        events = (
            db.query(Event)
            .filter(Event.end_time < now, Event.status != EventStatus.completed)
            .all()
        )

        for evt in events:
            evt.status = EventStatus.completed
        db.commit()
    finally:
        db.close()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Schedule the 'check_events_status' task to run periodically
    (e.g., every 60 seconds).
    """
    sender.add_periodic_task(
        60.0, check_events_status.s(), name="Check events status every minute"
    )
