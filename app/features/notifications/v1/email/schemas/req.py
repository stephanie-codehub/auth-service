from pydantic import BaseModel, EmailStr

from .enums import EmailTemplateType


class EmailNotificationRequest(BaseModel):
    to_address: EmailStr
    template_type: EmailTemplateType
