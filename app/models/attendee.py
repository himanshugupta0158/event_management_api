from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.schema import PrimaryKeyConstraint

from app.utils.mixins import BaseDBModel


class Attendee(BaseDBModel):
    __tablename__ = "attendees"

    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = mapped_column(Integer, ForeignKey("events.id"), nullable=False)
    check_in_status = mapped_column(Boolean, default=False)

    # Composite primary key on user_id and event_id
    __table_args__ = (PrimaryKeyConstraint("user_id", "event_id", name="pk_attendee"),)

    event = relationship("Event", back_populates="attendees")
    user = relationship("User", back_populates="attendees")
