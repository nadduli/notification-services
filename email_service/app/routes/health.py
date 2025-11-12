from fastapi import APIRouter, HTTPException, status

from app.domain.schemas import ApiResponse
from app.infrastructure.rabbitmq import get_connection
from app.infrastructure.redis import get_redis

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def health_check() -> ApiResponse:
    redis = await get_redis()
    try:
        await redis.ping()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Redis unavailable: {exc}")

    connection = await get_connection()
    if connection.is_closed:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="RabbitMQ connection closed")

    return ApiResponse(success=True, message="Service healthy")