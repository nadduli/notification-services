import logging
import sys
from typing import Any, Dict

import structlog


def configure_logging(level: str = "INFO") -> None:
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(stream=sys.stdout, level=level, format="%(message)s")


def bind_context(**kwargs: Any) -> Dict[str, Any]:
    return structlog.contextvars.bind_contextvars(**kwargs)