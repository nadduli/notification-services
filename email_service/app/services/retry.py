import asyncio
import math
import random
from contextlib import asynccontextmanager
from typing import AsyncIterator

from redis.asyncio import Redis

from app.settings import get_settings

_settings = get_settings()


class RetryContext:
    def __init__(self, redis: Redis, request_id: str) -> None:
        self.redis = redis
        self.request_id = request_id
        self.key = f"retry_attempt:{request_id}"

    async def get_attempt(self) -> int:
        attempt = await self.redis.incr(self.key)
        await self.redis.expire(self.key, _settings.redis_request_ttl)
        return int(attempt)

    async def clear(self) -> None:
        await self.redis.delete(self.key)

    def calculate_backoff(self, attempt: int) -> float:
        delay = min(
            _settings.retry_base_delay * math.pow(2, attempt - 1),
            _settings.retry_max_delay,
        )
        jitter = random.uniform(0, _settings.retry_base_delay)
        return delay + jitter


@asynccontextmanager
async def retry_operation(context: RetryContext) -> AsyncIterator[int]:
    attempt = await context.get_attempt()
    try:
        yield attempt
    except Exception:
        if attempt >= _settings.retry_max_attempts:
            raise
        backoff = context.calculate_backoff(attempt)
        await asyncio.sleep(backoff)
        raise
    finally:
        if attempt == 1:
            await context.clear()