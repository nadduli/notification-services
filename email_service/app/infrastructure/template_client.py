from typing import Any, Dict, Optional

import aiohttp

from app.domain.schemas import NotificationPayload
from app.settings import get_settings

_settings = get_settings()


class TemplateClient:
    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.base_url = str(_settings.template_service_url).rstrip("/")
        self.session = session

    async def render(self, payload: NotificationPayload, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        body = {
            "template_code": payload.template_code,
            "variables": payload.variables.model_dump(),
            "metadata": payload.metadata.model_dump(),
            "locale": payload.metadata.locale,
        }
        headers = {
            "Authorization": f"Bearer {_settings.template_service_token}",
            "Content-Type": "application/json",
        }
        if correlation_id:
            headers["X-Correlation-Id"] = correlation_id

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/v1/templates/render",
                json=body,
                headers=headers,
                timeout=10,
            ) as response:
                response.raise_for_status()
                return await response.json()