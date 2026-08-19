import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    phone_number: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
