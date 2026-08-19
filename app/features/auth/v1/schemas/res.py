from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str = Field(exclude=True)
    token_type: str = Field(default="bearer")
