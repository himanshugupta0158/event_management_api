from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, relationship

from app.utils.mixins import BaseDBModel


class Attendee(BaseDBModel):
    __tablename__ = "attendees"

    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = mapped_column(Integer, ForeignKey("events.id"), nullable=False)
    check_in_status = mapped_column(Boolean, default=False)

    event = relationship("Event", back_populates="attendees")
    user = relationship("User", back_populates="attendees")
