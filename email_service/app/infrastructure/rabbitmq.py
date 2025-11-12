from contextlib import asynccontextmanager
from typing import AsyncIterator

from aio_pika import ExchangeType, RobustChannel, RobustConnection, connect_robust

from app.settings import get_settings

_settings = get_settings()
_connection: RobustConnection | None = None


async def get_connection() -> RobustConnection:
    global _connection
    if _connection is None:
        _connection = await connect_robust(_settings.rabbitmq_url)
    return _connection


async def get_channel(prefetch: int = 10) -> RobustChannel:
    connection = await get_connection()
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=prefetch)
    return channel


async def ensure_core_exchanges(channel: RobustChannel) -> None:
    await channel.declare_exchange(_settings.notifications_exchange, ExchangeType.DIRECT, durable=True)
    await channel.declare_exchange(_settings.rabbitmq_retry_exchange, ExchangeType.DIRECT, durable=True)
    await channel.declare_exchange(_settings.rabbitmq_dead_letter_exchange, ExchangeType.DIRECT, durable=True)


@asynccontextmanager
async def rabbitmq_lifespan() -> AsyncIterator[RobustConnection]:
    connection = await get_connection()
    try:
        yield connection
    finally:
        await connection.close()