import asyncio

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.infrastructure.redis import get_redis
from app.infrastructure.status_repository import StatusRepository
from app.infrastructure.template_client import TemplateClient
from app.logging import configure_logging
from app.routes import health, notifications
from app.services.email_consumer import EmailQueueConsumer
from app.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="Email Service",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(health.router)
app.include_router(notifications.router)

if settings.prometheus_enabled:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.on_event("startup")
async def startup_event() -> None:
    redis = await get_redis()
    status_repo = StatusRepository(redis, ttl_seconds=settings.redis_request_ttl)
    template_client = TemplateClient()
    consumer = EmailQueueConsumer(status_repo=status_repo, template_client=template_client)
    asyncio.create_task(consumer.start())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    redis = await get_redis()
    await redis.close()
