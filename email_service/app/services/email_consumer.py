import json
from typing import Any, Dict, Optional

from aio_pika import ExchangeType, IncomingMessage, Message
from structlog import get_logger

from app.domain.schemas import NotificationPayload, NotificationStatus
from app.infrastructure.rabbitmq import ensure_core_exchanges, get_channel
from app.infrastructure.status_repository import StatusRepository
from app.infrastructure.template_client import TemplateClient
from app.logging import bind_context
from app.services.circuit_breaker import AsyncCircuitBreaker
from app.services.email_sender import EmailSender
from app.services.retry import RetryContext, retry_operation
from app.settings import get_settings

log = get_logger()
settings = get_settings()


class EmailQueueConsumer:
    def __init__(self, status_repo: StatusRepository, template_client: TemplateClient) -> None:
        self.status_repo = status_repo
        self.template_client = template_client
        self.sender = EmailSender()
        self.breaker = AsyncCircuitBreaker()

    async def start(self) -> None:
        channel = await get_channel()
        await ensure_core_exchanges(channel)

        queue = await channel.declare_queue(
            settings.rabbitmq_email_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.rabbitmq_dead_letter_exchange,
                "x-dead-letter-routing-key": "email.dead",
            },
        )

        notifications_exchange = await channel.get_exchange(settings.notifications_exchange)
        await queue.bind(notifications_exchange, routing_key="email")

        await queue.consume(self._process_message, no_ack=False)

    async def _process_message(self, message: IncomingMessage) -> None:
        headers = message.headers or {}
        correlation_id = headers.get("x-correlation-id")
        request_id_header = headers.get("x-request-id")

        async with message.process(ignore_processed=True, requeue=False):
            payload = NotificationPayload.model_validate_json(message.body)
            bind_context(
                request_id=payload.request_id,
                correlation_id=correlation_id or payload.metadata.correlation_id,
                user_id=str(payload.user_id),
            )
            log.info("email.consumer.received")

            if request_id_header and request_id_header != payload.request_id:
                log.warning("email.consumer.request_id_mismatch")
                return

            is_duplicate = await self.status_repo.ensure_idempotent(payload.request_id)
            if is_duplicate:
                log.info("email.consumer.duplicate_skipped")
                return

            retry_context = RetryContext(redis=self.status_repo.redis, request_id=payload.request_id)

            try:
                async with retry_operation(retry_context):
                    rendered = await self.breaker.call(
                        self.template_client.render,
                        payload,
                        correlation_id=correlation_id,
                    )

                    recipient = payload.metadata.recipient_email
                    subject = rendered.get("subject") or (payload.metadata.extra or {}).get("subject", "")
                    body = rendered.get("body")

                    await self.breaker.call(
                        self.sender.send,
                        recipient=recipient,
                        subject=subject,
                        body=body,
                        metadata=payload.metadata.model_dump(),
                    )
            except Exception as exc:
                log.exception("email.consumer.failed", error=str(exc))
                await self.status_repo.set_status(
                    payload.request_id,
                    NotificationStatus.failed,
                    error=str(exc),
                )
                await self._schedule_retry(message, headers, exc)
                raise
            else:
                await self.status_repo.set_status(payload.request_id, NotificationStatus.delivered)
                log.info("email.consumer.delivered")
                await self._publish_status_event(message, payload.request_id, "delivered", correlation_id)

    async def _schedule_retry(
        self,
        message: IncomingMessage,
        headers: Dict[str, Any],
        exc: Exception,
    ) -> None:
        attempt = int(headers.get("x-retry-attempt", 0)) + 1
        new_headers = {
            **headers,
            "x-retry-attempt": attempt,
            "x-error": str(exc),
        }

        retry_exchange = await message.channel.get_exchange(settings.rabbitmq_retry_exchange)
        retry_message = Message(
            body=message.body,
            headers=new_headers,
            content_type="application/json",
        )

        await retry_exchange.publish(
            retry_message,
            routing_key=settings.rabbitmq_email_queue,
            declare=[(settings.rabbitmq_retry_exchange, ExchangeType.DIRECT)],
        )

    async def _publish_status_event(
        self,
        message: IncomingMessage,
        request_id: str,
        status_value: str,
        correlation_id: Optional[str],
    ) -> None:
        status_exchange_name = getattr(settings, "status_exchange", None)
        if not status_exchange_name:
            return

        channel = message.channel
        status_exchange = await channel.declare_exchange(status_exchange_name, ExchangeType.DIRECT, durable=True)
        payload = json.dumps({"request_id": request_id, "status": status_value}).encode()

        await status_exchange.publish(
            Message(
                body=payload,
                headers={"x-correlation-id": correlation_id or request_id},
                content_type="application/json",
            ),
            routing_key="email.status",
        )