import csv
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependency import get_current_user
from app.models.attendee import Attendee
from app.models.event import Event
from app.models.user import User
from app.repositories.attendee_repo import (
    check_in_attendee,
    list_attendees,
    register_attendee,
)
from app.schemas.attendees import AttendeeCreate, AttendeeResponse

router = APIRouter(prefix="/attendees", tags=["Attendees"])


@router.post("/{event_id}/register", response_model=AttendeeResponse)
async def register_attendee_route(
    event_id: int,
    attendee_data: AttendeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Must be authenticated
):
    attendee, error = await register_attendee(db, event_id, attendee_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return attendee


@router.post("/{event_id}/checkin")
async def check_in_attendee_route(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attendee = await check_in_attendee(db, current_user.id, event_id)
    if not attendee:
        raise HTTPException(
            status_code=404, detail="Attendee not found for current user"
        )
    return {"message": "Check-in successful"}


@router.post("/{event_id}/checkin_bulk", response_model=List[AttendeeResponse])
async def check_in_attendees_bulk(
    event_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Optionally require auth
):
    """
    Expects a CSV file containing a list of attendee emails to check in.
    Example CSV content:
        email
        person1@example.com
        person2@example.com
    """
    event_query = await db.execute(select(Event).where(Event.id == event_id))
    event = event_query.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    contents = await file.read()
    lines = contents.decode().splitlines()
    csv_reader = csv.DictReader(lines)

    updated_attendees = []
    for row in csv_reader:
        email = row.get("email")
        if not email:
            continue

        attendee_query = (
            select(Attendee)
            .join(User, Attendee.user)
            .where(Attendee.event_id == event_id, User.email == email)
        )
        result = await db.execute(attendee_query)
        attendee = result.scalar_one_or_none()
        if attendee:
            attendee.check_in_status = True
            updated_attendees.append(attendee)

    db.commit()
    for att in updated_attendees:
        db.refresh(att)
    return updated_attendees


@router.get("/{event_id}/list", response_model=List[AttendeeResponse])
async def list_attendees_route(
    event_id: int,
    check_in_status: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attendees = await list_attendees(db, event_id, check_in_status)
    return attendees
