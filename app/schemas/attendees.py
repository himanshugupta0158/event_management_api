from typing import List, Optional

from pydantic import BaseModel, EmailStr


class AttendeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str


class AttendeeResponse(AttendeeCreate):
    attendee_id: int
    event_id: int
    check_in_status: bool

    class Config:
        orm_mode = True
