from pydantic import EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    api_name: str = "Auth Service"
    api_version: str = "v1.0.0"
    api_base_url: str
    api_log_level: str = "INFO"

    database_url: SecretStr
    test_database_url: str

    jwt_secret_key: SecretStr
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    jwt_algorithm: str = "HS256"

    activation_token_expire_days: int = 2
    password_reset_token_expire_hours: int = 36
    resend_api_key: SecretStr
    sender_email: EmailStr

    allowed_hosts: list[str]
    allowed_origins: list[str]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = AppSettings()  # type: ignore
