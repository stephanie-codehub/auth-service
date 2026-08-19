import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from pydantic import SecretStr

from app.core.config import settings
from app.features.users.v1.schemas.enums import UserRole


@dataclass
class TokenData:
    user_id: uuid.UUID
    roles: list[UserRole]


def create_access_token(user_id: uuid.UUID, user_roles: list[UserRole]) -> str:
    expire_at = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode = {
        "sub": str(user_id),
        "roles": user_roles,
        "exp": expire_at,
    }

    access_token = jwt.encode(
        to_encode,
        settings.jwt_secret_key.get_secret_value(),
        settings.jwt_algorithm,
    )
    return access_token


def decode_access_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("sub")
        roles = payload.get("roles")
        if user_id is None or roles is None:
            return None

        return TokenData(user_id=uuid.UUID(user_id), roles=list(roles))
    except (jwt.PyJWTError, ValueError):
        return None


def hash_password(password: SecretStr | str) -> str:
    password_bytes = (
        password.get_secret_value().encode("utf-8")
        if isinstance(password, SecretStr)
        else password.encode("utf-8")
    )
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: SecretStr, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.get_secret_value().encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
