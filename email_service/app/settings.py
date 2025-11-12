#!/usr/bin/python3
"""Settings module for email service"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl


class Settings(BaseSettings):
    """Settings class """
    service_name: str = "email_service"
    service_host: str = "0.0.0.0"
    service_port: int = 8001
    log_level: str = Field("INFO", env="LOG_LEVEL")
    prometheus_enabled: bool = Field(True, env="PROMETHEUS_ENABLED")

    notifications_exchange: str = Field("notifications.direct", env="NOTIFICATIONS_EXCHANGE")
    rabbitmq_url: str = Field(..., env="RABBITMQ_URL")
    rabbitmq_email_queue: str = Field("email.queue", env="RABBITMQ_EMAIL_QUEUE")
    rabbitmq_retry_exchange: str = Field("notifications.retry", env="RABBITMQ_RETRY_EXCHANGE")
    rabbitmq_dead_letter_exchange: str = Field("notifications.dlx", env="RABBITMQ_DLX")

    # redis
    redis_url: str = Field(..., env="REDIS_URL")
    redis_request_ttl: int = Field(600, env="REDIS_REQUEST_TTL")

    # template service
    template_service_url: HttpUrl = Field(..., env="TEMPLATE_SERVICE_URL")
    template_service_token: str = Field(..., env="TEMPLATE_SERVICE_TOKEN")

    # email (smtp)
    smtp_host: str = Field(..., env="SMTP_HOST")
    smtp_port: int = Field(587, env="SMTP_PORT")
    smtp_username: str = Field(..., env="SMTP_USERNAME")
    smtp_password: str = Field(..., env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(True, env="SMTP_USE_TLS")

    # resilience
    circuit_breaker_fail_max: int = Field(5, env="CIRCUIT_BREAKER_FAIL_MAX")
    circuit_breaker_reset_timeout: int = Field(60, env="CIRCUIT_BREAKER_RESET_TIMEOUT")
    retry_base_delay: float = Field(1.0, env="RETRY_BASE_DELAY")
    retry_max_delay: float = Field(60.0, env="RETRY_MAX_DELAY")
    retry_max_attempts: int = Field(5, env="RETRY_MAX_ATTEMPTS")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")