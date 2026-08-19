from pydantic import BaseModel, EmailStr, Field


class UserFilterParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    is_active: bool | None = None
    user_role: str | None = None
