from pydantic import BaseModel, EmailStr, Field, SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber

PhoneNumber.phone_format = "E164"


class UpdateUserProfile(BaseModel):
    email: EmailStr | None = Field(default=None)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone_number: PhoneNumber | None = Field(default=None)


class ChangePasswordRequest(BaseModel):
    new_password: SecretStr = Field(min_length=8, max_length=100)
    current_password: SecretStr
