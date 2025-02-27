from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependency import get_current_user
from app.models.user import User
from app.repositories.event_repo import EventRepository, get_event_repo
from app.schemas.event import EventCreate, EventResponse, EventStatus, EventUpdate
from app.utils.response_format import APIResponse

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=APIResponse, status_code=201)
async def create_event_route(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    event_repo: EventRepository = Depends(get_event_repo),
):
    new_evt = await event_repo.create_event(event)
    return APIResponse(
        message="Event created successfully",
        data=EventResponse.serialize(new_evt),
    )


@router.get("/", response_model=APIResponse, status_code=200)
async def list_events_route(
    status: Optional[EventStatus] = None,
    location: Optional[str] = None,
    date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    event_repo: EventRepository = Depends(get_event_repo),
):
    events = await event_repo.list_events(status, location, date)
    return APIResponse(
        message="Events fetched successfully",
        data=[EventResponse.serialize(event) for event in events],
    )


@router.get("/{event_id}", response_model=APIResponse, status_code=200)
async def get_event_route(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    event_repo: EventRepository = Depends(get_event_repo),
):
    event = await event_repo.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return APIResponse(
        message="Event fetched successfully",
        data=EventResponse.serialize(event),
    )


@router.put("/{event_id}", response_model=APIResponse, status_code=200)
async def update_event_route(
    event_id: int,
    event_update_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    event_repo: EventRepository = Depends(get_event_repo),
):
    updated_evt = await event_repo.update_event(event_id, event_update_data)
    if not updated_evt:
        raise HTTPException(status_code=404, detail="Event not found")
    return APIResponse(
        message="Event updated successfully",
        data=EventResponse.serialize(updated_evt),
    )


@router.delete("/{event_id}", response_model=APIResponse, status_code=200)
async def delete_event_route(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    event_repo: EventRepository = Depends(get_event_repo),
):
    deleted_evt = await event_repo.delete_event(event_id)
    return APIResponse(
        message="Event deleted successfully",
        data={"event_id": deleted_evt.id},
    )
