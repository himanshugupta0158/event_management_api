from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.models.event import Event, EventStatus
from app.schemas.event import EventCreate, EventUpdate


async def create_event(db: Session, event_data: EventCreate) -> Event:
    # Convert string date/time to datetime objects
    date_obj = datetime.strptime(event_data.date, "%d/%m/%Y").date()
    start_time_obj = datetime.strptime(event_data.start_time, "%I:%M %p").time()
    end_time_obj = datetime.strptime(event_data.end_time, "%I:%M %p").time()

    # Combine date and time into datetime objects
    start_datetime = datetime.combine(date_obj, start_time_obj)
    end_datetime = datetime.combine(date_obj, end_time_obj)

    # Check if an event with same details already exists
    existing_event_query = select(Event).where(
        Event.name == event_data.name,
        Event.location == event_data.location,
        Event.start_time == start_datetime,
        Event.end_time == end_datetime,
    )
    existing_event = db.execute(existing_event_query).scalar_one_or_none()
    if existing_event:
        raise HTTPException(
            status_code=400, detail="An event with the same details already exists"
        )

    event_dict = event_data.model_dump()
    event_dict.pop("date")
    event_dict.update({"start_time": start_datetime, "end_time": end_datetime})

    new_event = Event(**event_dict)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


async def list_events(
    db: Session, status: EventStatus = None, location: str = None, date: datetime = None
) -> list[Event]:
    now = datetime.utcnow()

    # Mark events as completed if end_time < now and they are not completed
    update_stmt = text(
        """
        UPDATE events
        SET status = :completed
        WHERE status != :completed
          AND end_time < :current_time
        """
    )
    db.execute(
        update_stmt,
        {
            "completed": EventStatus.completed,
            "current_time": now,
        },
    )
    db.commit()

    query = select(Event)
    if status:
        query = query.where(Event.status == status)
    if location:
        query = query.where(Event.location.ilike(f"%{location}%"))
    if date:
        query = query.where(Event.start_time <= date, Event.end_time >= date)

    result = db.execute(query)
    return result.scalars().all()


async def get_event(db: Session, event_id: int) -> Event:
    query = select(Event).where(Event.id == event_id)
    result = db.execute(query)
    return result.scalar_one_or_none()


async def update_event(db: Session, event_id: int, event_update: EventUpdate) -> Event:
    event = await get_event(db, event_id)
    if not event:
        return None

    update_data = event_update.dict(exclude_unset=True)

    # Handle date and time conversions if present
    if all(key in update_data for key in ["date", "start_time", "end_time"]):
        # Convert string date/time to datetime objects
        date_obj = datetime.strptime(update_data["date"], "%d/%m/%Y").date()
        start_time_obj = datetime.strptime(update_data["start_time"], "%I:%M %p").time()
        end_time_obj = datetime.strptime(update_data["end_time"], "%I:%M %p").time()

        # Combine date and time into datetime objects
        update_data["start_time"] = datetime.combine(date_obj, start_time_obj)
        update_data["end_time"] = datetime.combine(date_obj, end_time_obj)

        # Remove the date field as it's been combined with times
        update_data.pop("date")

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event


async def delete_event(db: Session, event_id: int) -> Event:
    event = await get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return event
