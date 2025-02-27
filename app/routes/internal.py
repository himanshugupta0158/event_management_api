from fastapi import APIRouter, Depends

from app.repositories.event_repo import EventRepository, get_event_repo
from app.utils.response_format import APIResponse

router = APIRouter(prefix="/internal", tags=["Internal"])


@router.get("/event-checker", response_model=APIResponse, status_code=200)
async def event_checker_route(
    event_repo: EventRepository = Depends(get_event_repo),
):
    await event_repo.check_events_status()
    return APIResponse(message="Updated events status")
