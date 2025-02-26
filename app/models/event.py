from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import mapped_column, relationship

from app.utils.constants import EventStatus
from app.utils.mixins import BaseDBModel


class Event(BaseDBModel):
    __tablename__ = "events"

    name = mapped_column(String(200), nullable=False)
    description = mapped_column(String)
    start_time = mapped_column(DateTime, nullable=False)
    end_time = mapped_column(DateTime, nullable=False)
    location = mapped_column(String(255), nullable=False)
    max_attendees = mapped_column(Integer, nullable=False)
    status = mapped_column(Enum(EventStatus), default=EventStatus.scheduled)

    attendees = relationship("Attendee", back_populates="event")
