from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependency import get_current_user
from app.models.user import User
from app.repositories.event_repo import (
    create_event,
    delete_event,
    get_event,
    list_events,
    update_event,
)
from app.schemas.event import EventCreate, EventResponse, EventStatus, EventUpdate
from app.utils.response_format import APIResponse

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=APIResponse, status_code=201)
async def create_event_route(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_evt = await create_event(db, event)
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
):
    events = await list_events(db, status, location, date)
    return APIResponse(
        message="Events fetched successfully",
        data=[EventResponse.serialize(event) for event in events],
    )


@router.get("/{event_id}", response_model=APIResponse, status_code=200)
async def get_event_route(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = await get_event(db, event_id)
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
):
    updated_evt = await update_event(db, event_id, event_update_data)
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
):
    deleted_evt = await delete_event(db, event_id)
    return APIResponse(
        message="Event deleted successfully",
        data={"event_id": deleted_evt.id},
    )
