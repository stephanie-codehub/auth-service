from pydantic import BaseModel, EmailStr, Field, SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber

PhoneNumber.phone_format = "E164"


class UserRegister(BaseModel):
    password: SecretStr = Field(min_length=8, max_length=100)
    email: EmailStr
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    phone_number: PhoneNumber


class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr


class InitiatePasswordReset(BaseModel):
    email: EmailStr


class CompletePasswordReset(BaseModel):
    token: str
    new_password: SecretStr = Field(min_length=8, max_length=100)
