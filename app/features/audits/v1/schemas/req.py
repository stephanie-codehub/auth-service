import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AuditLogFilterParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    activity_type: str | None = None
    activity_status: str | None = None
    device_type: str | None = None
    device_name: str | None = None
    location: str | None = None
    ip_address: str | None = None
    user_id: uuid.UUID | None = None
    timestamp: datetime | None = None
