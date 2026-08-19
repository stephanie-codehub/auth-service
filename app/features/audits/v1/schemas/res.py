import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.features.audits.v1.schemas.enums import ActivityStatus, ActivityType


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    activity_type: ActivityType
    activity_status: ActivityStatus
    device_type: str
    device_name: str
    location: str
    ip_address: str
    user_id: uuid.UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
