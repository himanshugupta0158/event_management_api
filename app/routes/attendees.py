from io import BytesIO
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder

from app.core.dependency import get_current_user
from app.models.user import User
from app.repositories.attendee_repo import AttendeeRepository, get_attendee_repo
from app.utils.response_format import APIResponse

router = APIRouter(prefix="/attendees", tags=["Attendees"])


@router.post("/{event_id}/register", response_model=APIResponse)
async def register_attendee_route(
    event_id: int,
    attendee_repo: AttendeeRepository = Depends(get_attendee_repo),
    current_user: User = Depends(get_current_user),
):

    attendee, error = await attendee_repo.register_attendee(event_id, current_user)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return APIResponse(
        message="Attendee registered successfully",
        data=jsonable_encoder(attendee),
    )


@router.post("/{event_id}/checkin", response_model=APIResponse, status_code=200)
async def check_in_attendee_route(
    event_id: int,
    attendee_repo: AttendeeRepository = Depends(get_attendee_repo),
    current_user: User = Depends(get_current_user),
):
    attendee = await attendee_repo.check_in_attendee(current_user.id, event_id)
    if not attendee:
        raise HTTPException(
            status_code=404, detail="Attendee not found for current user"
        )
    return APIResponse(
        message="Check-in successful",
        data=jsonable_encoder(attendee),
    )


@router.post("/{event_id}/checkin_bulk", response_model=APIResponse)
async def check_in_attendees_bulk(
    event_id: int,
    file: UploadFile = File(...),
    attendee_repo: AttendeeRepository = Depends(get_attendee_repo),
    current_user: User = Depends(get_current_user),
):
    """
    Expects a CSV or Excel file containing a list of attendee emails to check in.
    Example CSV/Excel content:
        email
        person1@example.com
        person2@example.com
    """
    contents = await file.read()

    if file.filename.endswith(".csv"):
        df = pd.read_csv(BytesIO(contents))
    elif file.filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(BytesIO(contents))
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type, Only CSV and Excel are supported",
        )

    emails = df["email"].dropna().tolist()

    result = await attendee_repo.bulk_check_in_by_emails(event_id, emails)
    return APIResponse(
        message="Check-in successful",
        data=jsonable_encoder(result),
    )


@router.get("/{event_id}/list", response_model=APIResponse)
async def list_attendees_route(
    event_id: int,
    check_in_status: Optional[bool] = None,
    attendee_repo: AttendeeRepository = Depends(get_attendee_repo),
    current_user: User = Depends(get_current_user),
):
    attendees = await attendee_repo.list_attendees(event_id, check_in_status)
    return APIResponse(
        message="Attendees listed successfully",
        data=jsonable_encoder(attendees),
    )
