from datetime import datetime
from typing import List, Optional

from fastapi import Depends, HTTPException
from sqlalchemy import and_, select, update
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.event import Event, EventStatus
from app.schemas.event import EventCreate, EventUpdate


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create_event(self, event_data: EventCreate) -> Event:
        date_obj = datetime.strptime(event_data.date, "%d/%m/%Y").date()
        start_time_obj = datetime.strptime(event_data.start_time, "%I:%M %p").time()
        end_time_obj = datetime.strptime(event_data.end_time, "%I:%M %p").time()

        start_datetime = datetime.combine(date_obj, start_time_obj)
        end_datetime = datetime.combine(date_obj, end_time_obj)

        query = select(Event).where(
            and_(
                Event.name == event_data.name,
                Event.location == event_data.location,
                Event.start_time == start_datetime,
                Event.end_time == end_datetime,
            )
        )
        existing_event = self.db.execute(query).scalar_one_or_none()
        if existing_event:
            raise HTTPException(
                status_code=400, detail="An event with the same details already exists"
            )

        event_dict = event_data.model_dump()
        event_dict.pop("date")
        event_dict.update({"start_time": start_datetime, "end_time": end_datetime})

        new_event = Event(**event_dict)
        self.db.add(new_event)
        self.db.commit()
        self.db.refresh(new_event)
        return new_event

    async def list_events(
        self,
        status: Optional[EventStatus] = None,
        location: Optional[str] = None,
        date: Optional[datetime] = None,
    ) -> List[Event]:
        now = datetime.now()

        query = (
            update(Event)
            .where(and_(Event.status != EventStatus.completed, Event.end_time < now))
            .values(status=EventStatus.completed)
        )
        self.db.execute(query)
        self.db.commit()

        query = select(Event)
        conditions = []

        if status:
            conditions.append(Event.status == status)
        if location:
            conditions.append(Event.location.ilike(f"%{location}%"))
        if date:
            conditions.extend([Event.start_time <= date, Event.end_time >= date])

        if conditions:
            query = query.where(and_(*conditions))

        result = self.db.execute(query)
        return result.scalars().all()

    async def get_event(self, event_id: int) -> Optional[Event]:
        query = select(Event).where(Event.id == event_id)
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_event(
        self, event_id: int, event_update: EventUpdate
    ) -> Optional[Event]:
        event = await self.get_event(event_id)
        if not event:
            return None

        update_data = event_update.dict(exclude_unset=True)

        if all(key in update_data for key in ["date", "start_time", "end_time"]):
            date_obj = datetime.strptime(update_data["date"], "%d/%m/%Y").date()
            start_time_obj = datetime.strptime(
                update_data["start_time"], "%I:%M %p"
            ).time()
            end_time_obj = datetime.strptime(update_data["end_time"], "%I:%M %p").time()

            update_data["start_time"] = datetime.combine(date_obj, start_time_obj)
            update_data["end_time"] = datetime.combine(date_obj, end_time_obj)
            update_data.pop("date")

        query = (
            update(Event)
            .where(Event.id == event_id)
            .values(**update_data)
            .returning(Event)
        )
        result = self.db.execute(query)
        self.db.commit()
        return result.scalar_one()

    async def delete_event(self, event_id: int) -> Event:
        event = await self.get_event(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        self.db.delete(event)
        self.db.commit()
        return event

    async def check_events_status(self):
        now = datetime.now()
        query = (
            update(Event)
            .where(and_(Event.end_time < now, Event.status != EventStatus.completed))
            .values(status=EventStatus.completed)
            .returning(Event)
        )
        self.db.execute(query)
        self.db.commit()


def get_event_repo(db: Session = Depends(get_db)):
    return EventRepository(db)
