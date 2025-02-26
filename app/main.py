import uvicorn
from fastapi import FastAPI

from app.core.database import Base, engine
from app.routes import attendees, auth, event

# Create tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Management API")

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(event.router, prefix="/api/v1")
app.include_router(attendees.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "OK"}
