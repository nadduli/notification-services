from email.message import EmailMessage
from typing import Any, Dict

import aiosmtplib

from app.settings import get_settings

_settings = get_settings()


class EmailSender:
    def __init__(self) -> None:
        self.smtp_host = _settings.smtp_host
        self.smtp_port = _settings.smtp_port
        self.username = _settings.smtp_username
        self.password = _settings.smtp_password
        self.use_tls = _settings.smtp_use_tls

    async def send(self, recipient: str, subject: str, body: str, metadata: Dict[str, Any]) -> None:
        message = EmailMessage()
        message["From"] = self.username
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        await aiosmtplib.send(
            message,
            hostname=self.smtp_host,
            port=self.smtp_port,
            username=self.username,
            password=self.password,
            start_tls=self.use_tls,
        )