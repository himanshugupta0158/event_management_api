import traceback
from typing import List, Optional

from fastapi import Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.attendee import Attendee
from app.models.event import Event, EventStatus
from app.models.user import User


class AttendeeRepository:
    def __init__(self, db: Session):
        self.db = db

    async def register_attendee(self, event_id: int, user: User):
        try:
            event = await self.get_event(event_id)
            if not event:
                return None, "Event not found"

            if event.status == EventStatus.completed:
                return None, "Cannot register for completed event"

            existing_query = select(Attendee).where(
                Attendee.event_id == event_id,
                Attendee.user_id == user.id,
            )
            existing = await self.get_attendee(existing_query)
            if existing:
                return None, "Attendee already registered"

            current_count = await self.get_attendee_count(event_id)
            if current_count >= event.max_attendees:
                return None, "Max attendees reached"

            new_attendee = Attendee(event_id=event_id, user_id=user.id)
            return await self.save_attendee(new_attendee), None
        except Exception as e:
            traceback.print_exc()
            return None, str(e)

    async def check_in_attendee(self, user_id: int, event_id: int):
        event = await self.get_event(event_id)
        if not event:
            return None
        if event.status == EventStatus.completed:
            return None

        query = select(Attendee).where(
            Attendee.user_id == user_id, Attendee.event_id == event_id
        )
        attendee = await self.get_attendee(query)
        if attendee:
            attendee.check_in_status = True
            return await self.save_attendee(attendee)
        return None

    async def bulk_check_in_by_emails(self, event_id: int, emails: List[str]):
        event = await self.get_event(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        if event.status == EventStatus.completed:
            raise HTTPException(status_code=400, detail="Event is completed")

        result = {"success": [], "failed": []}
        for email in emails:
            attendee_query = (
                select(Attendee)
                .join(User, Attendee.user)
                .where(Attendee.event_id == event_id, User.email == email)
            )
            attendee = await self.get_attendee(attendee_query)
            if attendee:
                if not attendee.check_in_status:
                    attendee.check_in_status = True
                    updated_attendee = await self.save_attendee(attendee)
                    result["success"].append(
                        {
                            "email": updated_attendee.user.email,
                            "message": "Check-in successful.",
                        }
                    )
                else:
                    result["failed"].append(
                        {"email": email, "message": "Attendee already checked in."}
                    )
            else:
                result["failed"].append(
                    {"email": email, "message": "No attendee found for this email."}
                )

        return result

    async def list_attendees(
        self, event_id: int, check_in_status: Optional[bool] = None
    ):
        event = await self.get_event(event_id)
        if not event:
            return []

        query = select(Attendee).where(Attendee.event_id == event_id)
        if check_in_status is not None:
            query = query.where(Attendee.check_in_status == check_in_status)
        result = self.db.execute(query)
        return result.scalars().all()

    async def get_event(self, event_id: int):
        query = select(Event).where(Event.id == event_id)
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_attendee(self, query):
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_attendee_count(self, event_id: int) -> int:
        query = select(func.count(Attendee.event_id)).where(
            Attendee.event_id == event_id
        )
        result = self.db.execute(query)
        return result.scalar() or 0

    async def save_attendee(self, attendee: Attendee):
        self.db.add(attendee)
        self.db.commit()
        self.db.refresh(attendee)
        return attendee


def get_attendee_repo(db: Session = Depends(get_db)):
    return AttendeeRepository(db)
