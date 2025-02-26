import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_register_attendee():
    # First create an event
    event_resp = client.post("/events/", json={
        "name": "Attendee Test Event",
        "description": "Event for Attendee Testing",
        "start_time": "2030-02-01T10:00:00",
        "end_time": "2030-02-01T12:00:00",
        "location": "Testing Hall",
        "max_attendees": 2
    })
    assert event_resp.status_code == 200
    event_data = event_resp.json()
    event_id = event_data["event_id"]

    # Now register an attendee
    attendee_resp = client.post(f"/attendees/{event_id}/register", json={
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "phone_number": "1234567890"
    })
    assert attendee_resp.status_code == 200
    attendee_data = attendee_resp.json()
    assert attendee_data["email"] == "alice@example.com"
    assert attendee_data["check_in_status"] is False
