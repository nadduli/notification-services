from typing import Any, Awaitable, Callable, TypeVar

from aiobreaker import CircuitBreaker

from app.settings import get_settings

T = TypeVar("T")

_settings = get_settings()


class AsyncCircuitBreaker:
    def __init__(self, fail_max: int | None = None, reset_timeout: int | None = None) -> None:
        self.breaker = CircuitBreaker(
            fail_max or _settings.circuit_breaker_fail_max,
            reset_timeout or _settings.circuit_breaker_reset_timeout,
        )

    async def call(self, func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any) -> T:
        return await self.breaker.call_async(func, *args, **kwargs)

    @property
    def is_open(self) -> bool:
        return self.breaker.current_state == "open"

    @property
    def is_half_open(self) -> bool:
        return self.breaker.current_state == "half-open"

    @property
    def is_closed(self) -> bool:
        return self.breaker.current_state == "closed"