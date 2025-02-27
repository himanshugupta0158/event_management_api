from pydantic import BaseModel


class AttendeeResponse(BaseModel):
    attendee_id: int
    event_id: int
    check_in_status: bool

    class Config:
        orm_mode = True
