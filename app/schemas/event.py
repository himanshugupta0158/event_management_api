import enum
import re
from datetime import date as date_type
from datetime import datetime
from datetime import time as time_type
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator, validator

from app.models.event import Event


class EventStatus(str, enum.Enum):
    scheduled = "scheduled"
    ongoing = "ongoing"
    completed = "completed"
    canceled = "canceled"


class DateTimeBase(BaseModel):
    @classmethod
    def validate_date_format(cls, value: str) -> str:
        if not re.match(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$", value):
            raise ValueError("Date must be in DD/MM/YYYY format")
        date_obj = datetime.strptime(value, "%d/%m/%Y").date()
        if date_obj < datetime.now().date():
            raise ValueError("Date must be in the future")
        return value

    @classmethod
    def validate_time_format(cls, value: str) -> str:
        if not re.match(r"^(1[0-2]|0?[1-9]):[0-5][0-9]\s?(AM|PM)$", value):
            raise ValueError("Time must be in 12-hour format (HH:MM AM/PM)")
        return value


class EventCreate(DateTimeBase):
    name: str
    description: Optional[str] = None
    date: str
    start_time: str
    end_time: str
    location: str
    max_attendees: int

    @field_validator("date")
    def validate_date(cls, v):
        return cls.validate_date_format(v)

    @field_validator("start_time", "end_time")
    def validate_time(cls, v):
        return cls.validate_time_format(v)

    @field_validator("end_time")
    def validate_end_time(cls, v, info):
        if "start_time" in info.data:
            start = datetime.strptime(info.data["start_time"], "%I:%M %p")
            end = datetime.strptime(v, "%I:%M %p")
            if end <= start:
                raise ValueError("End time must be after start time")
        return v


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    max_attendees: Optional[int] = None
    status: Optional[EventStatus] = None

    @validator("date")
    def validate_date(cls, v):
        if v:
            try:
                datetime.strptime(v, "%d/%m/%Y")
                return v
            except ValueError:
                raise ValueError("Date must be in DD/MM/YYYY format")
        return v

    @validator("start_time", "end_time")
    def validate_time(cls, v):
        if v:
            try:
                datetime.strptime(v, "%I:%M %p")
                return v
            except ValueError:
                raise ValueError("Time must be in HH:MM AM/PM format")
        return v


class EventResponse(DateTimeBase):
    event_id: int
    name: str
    description: Optional[str]
    date: str  # Will be formatted as DD/MM/YYYY
    start_time: str  # Will be formatted as HH:MM AM/PM
    end_time: str  # Will be formatted as HH:MM AM/PM
    location: str
    max_attendees: int
    status: EventStatus

    model_config = ConfigDict(from_attributes=True)

    @field_validator("date", mode="before")
    def format_date(cls, v):
        if isinstance(v, (date_type, datetime)):
            return v.strftime("%d/%m/%Y")
        return v

    @field_validator("start_time", "end_time", mode="before")
    def format_time(cls, v):
        if isinstance(v, time_type):
            return v.strftime("%I:%M %p")
        return v

    @classmethod
    def serialize(cls, event: Event):
        return cls(
            event_id=event.id,
            name=event.name,
            description=event.description,
            date=event.start_time.date(),
            start_time=event.start_time.time(),
            end_time=event.end_time.time(),
            location=event.location,
            max_attendees=event.max_attendees,
            status=event.status,
        )
