from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, relationship

from app.utils.mixins import BaseDBModel


class User(BaseDBModel):
    __tablename__ = "users"

    username = mapped_column(String(150), unique=True, nullable=False, index=True)
    email = mapped_column(String(255), unique=True, nullable=False, index=True)
    first_name = mapped_column(String(100), nullable=False)
    last_name = mapped_column(String(100), nullable=False)
    phone_number = mapped_column(String(20), nullable=True)
    password = mapped_column(String(255), nullable=False)
    token_version = mapped_column(Integer, default=0, nullable=False)

    attendees = relationship("Attendee", back_populates="user")
