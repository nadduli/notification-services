from typing import Dict, Optional

from redis.asyncio import Redis

from app.domain.schemas import NotificationStatus


class StatusRepository:
    def __init__(self, redis: Redis, ttl_seconds: int):
        self.redis = redis
        self.ttl = ttl_seconds

    def _status_key(self, request_id: str) -> str:
        return f"notification_status:{request_id}"

    def _idempotency_key(self, request_id: str) -> str:
        return f"idempotency:{request_id}"

    async def set_status(
        self, request_id: str, status: NotificationStatus, error: Optional[str] = None
    ) -> None:
        payload: Dict[str, str] = {"status": status.value}
        if error:
            payload["error"] = error
        await self.redis.hset(self._status_key(request_id), mapping=payload)
        await self.redis.expire(self._status_key(request_id), self.ttl)

    async def get_status(self, request_id: str) -> Optional[Dict[str, str]]:
        data = await self.redis.hgetall(self._status_key(request_id))
        return data if data else None

    async def ensure_idempotent(self, request_id: str) -> bool:
        key = self._idempotency_key(request_id)
        result = await self.redis.setnx(key, "1")
        if result:
            await self.redis.expire(key, self.ttl)
        return not result