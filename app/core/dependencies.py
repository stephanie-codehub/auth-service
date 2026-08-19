from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from structlog.contextvars import bind_contextvars

from app.core.exceptions import InvalidAuthTokenException, ResourceNotFoundException
from app.core.security import TokenData, decode_access_token
from app.features.users.v1.dependencies import get_user_repo
from app.features.users.v1.models import User
from app.features.users.v1.repository import UserRepository
from app.features.users.v1.schemas.enums import UserRole

security_scheme = HTTPBearer(auto_error=False)


async def require_auth(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(security_scheme)
    ],
) -> TokenData:
    if not credentials:
        raise InvalidAuthTokenException()

    token_data = decode_access_token(credentials.credentials)
    if not token_data:
        raise InvalidAuthTokenException()

    bind_contextvars(
        user_id=token_data.user_id,
    )
    request.state.user_id = token_data.user_id
    return token_data


def require_roles(*allowed_roles: UserRole):
    """RBAC: Validates scopes via the decrypted JWT token"""

    async def role_checker(
        token_data: Annotated[TokenData, Depends(require_auth)],
    ) -> TokenData:
        allowed_role_strings = [role.value for role in allowed_roles]
        has_permission = any(role in token_data.roles for role in allowed_role_strings)

        if not has_permission:
            raise ResourceNotFoundException()

        return token_data

    return role_checker


def log_activity(activity: str):
    """Sets the audited action explicitly on the request for the audit log middleware"""

    async def activity_type_logger(request: Request):
        request.state.activity_type = activity

    return activity_type_logger


async def get_current_user(
    token_data: Annotated[TokenData, Depends(require_auth)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> User:
    user = await user_repo.get_user_profile_by_id(token_data.user_id)
    if not user or not user.is_active:
        raise InvalidAuthTokenException()
    return user


async def require_admin_role():
    return require_roles(UserRole.ADMIN)
