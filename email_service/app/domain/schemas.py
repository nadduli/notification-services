from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, HttpUrl


class NotificationType(str, Enum):
    email = "email"
    push = "push"


class NotificationStatus(str, Enum):
    delivered = "delivered"
    pending = "pending"
    failed = "failed"


class NotificationVariables(BaseModel):
    name: str
    link: HttpUrl
    meta: Optional[Dict[str, Any]] = None


class NotificationMetadata(BaseModel):
    recipient_email: EmailStr
    locale: Optional[str] = "en"
    correlation_id: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


class NotificationPayload(BaseModel):
    notification_type: NotificationType
    user_id: UUID
    template_code: str
    variables: NotificationVariables
    request_id: str
    priority: int = 5
    metadata: NotificationMetadata


class NotificationStatusUpdate(BaseModel):
    notification_id: str
    status: NotificationStatus
    timestamp: Optional[datetime] = None
    error: Optional[str] = None


class PaginationMeta(BaseModel):
    total: int = 0
    limit: int = 0
    page: int = 1
    total_pages: int = 0
    has_next: bool = False
    has_previous: bool = False


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: str
    meta: PaginationMeta = PaginationMeta()