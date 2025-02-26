import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_create_event():
    response = client.post("/events/", json={
        "name": "Test Event",
        "description": "A sample event",
        "start_time": "2030-01-01T10:00:00",
        "end_time": "2030-01-01T12:00:00",
        "location": "Sample Location",
        "max_attendees": 100
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Event"
    assert data["event_id"] is not None
    assert data["status"] == "scheduled"
