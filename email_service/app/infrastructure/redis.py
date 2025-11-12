from contextlib import asynccontextmanager
from typing import AsyncIterator

from redis.asyncio import Redis

from app.settings import get_settings

_settings = get_settings()
_client: Redis | None = None


async def get_redis() -> Redis:
    global _client
    if _client is None:
        _client = Redis.from_url(_settings.redis_url, decode_responses=True)
    return _client


@asynccontextmanager
async def redis_lifespan() -> AsyncIterator[Redis]:
    client = await get_redis()
    try:
        yield client
    finally:
        await client.close()
