from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.schemas import ApiResponse
from app.infrastructure.redis import get_redis
from app.infrastructure.status_repository import StatusRepository
from app.settings import get_settings

router = APIRouter(prefix="/notifications", tags=["notifications"])
settings = get_settings()


async def get_status_repo() -> StatusRepository:
    redis = await get_redis()
    return StatusRepository(redis, ttl_seconds=settings.redis_request_ttl)


@router.get("/{request_id}", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def get_notification_status(request_id: str, repo: StatusRepository = Depends(get_status_repo)) -> ApiResponse:
    status_payload = await repo.get_status(request_id)
    if not status_payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return ApiResponse(success=True, message="Notification status retrieved", data=status_payload)