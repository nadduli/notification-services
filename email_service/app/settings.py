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
    rabbitmq_url: str = Field(default="", env="RABBITMQ_URL")
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

    # User Service (for API key when calling user service if needed)
    user_service_api_key: str = Field(..., env="USER_SERVICE_API_KEY")
    user_service_url: HttpUrl = Field(default="http://localhost:8000", env="USER_SERVICE_URL")

    # PostgreSQL (if needed for direct DB access, though unlikely per requirements)
    postgres_db: str = Field("distributed_database", env="POSTGRES_DB")
    postgres_user: str = Field("shared_user", env="POSTGRES_USER")
    postgres_pass: str = Field("shared_password", env="POSTGRES_PASS")
    postgres_host: str = Field("localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")

    # RabbitMQ individual components (if RABBITMQ_URL not provided)
    rabbitmq_user: str = Field("guest", env="RABBITMQ_USER")
    rabbitmq_pass: str = Field("guest", env="RABBITMQ_PASS")
    rabbitmq_host: str = Field("localhost", env="RABBITMQ_HOST")
    rabbitmq_port: int = Field(5672, env="RABBITMQ_PORT")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def rabbitmq_connection_url(self) -> str:
        """Construct RabbitMQ URL from components if RABBITMQ_URL not provided"""
        if self.rabbitmq_url:
            return self.rabbitmq_url
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_pass}@{self.rabbitmq_host}:{self.rabbitmq_port}/"


def get_settings() -> Settings:
    return Settings()