from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.models.attendee import Attendee
from app.models.event import Event
from app.schemas.attendees import AttendeeCreate


async def register_attendee(db: Session, event_id: int, attendee_data: AttendeeCreate):
    # Ensure event exists
    event_query = select(Event).where(Event.id == event_id)
    event_result = db.execute(event_query)
    event = event_result.scalar_one_or_none()
    if not event:
        return None, "Event not found"

    # Check if attendee already registered
    existing_query = select(Attendee).where(
        Attendee.event_id == event_id,
        Attendee.user_id == None,  # Adjust logic if you link Attendee with user ID
    )
    # For an actual scenario, you'd match on a user or email. This snippet is simplified.
    existing = (db.execute(existing_query)).scalar_one_or_none()
    if existing:
        return None, "Attendee already registered"

    # Check event capacity
    count_query = select(func.count(Attendee.event_id)).where(
        Attendee.event_id == event_id
    )
    count_result = db.execute(count_query)
    current_count = count_result.scalar() or 0
    if current_count >= event.max_attendees:
        return None, "Max attendees reached"

    # Create new attendee
    new_attendee = Attendee(
        event_id=event_id,
        check_in_status=False,
    )
    db.add(new_attendee)
    db.commit()
    db.refresh(new_attendee)
    return new_attendee, None


async def check_in_attendee(db: Session, user_id: int, event_id: int):
    query = select(Attendee).where(
        Attendee.user_id == user_id, Attendee.event_id == event_id
    )
    result = db.execute(query)
    attendee = result.scalar_one_or_none()
    if attendee:
        attendee.check_in_status = True
        db.commit()
        db.refresh(attendee)
        return attendee
    return None


async def list_attendees(db: Session, event_id: int, check_in_status: bool = None):
    query = select(Attendee).where(Attendee.event_id == event_id)
    if check_in_status is not None:
        query = query.where(Attendee.check_in_status == check_in_status)
    result = db.execute(query)
    return result.scalars().all()
