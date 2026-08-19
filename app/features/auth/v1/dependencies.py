from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_session
from app.features.auth.v1.service import AuthService
from app.features.notifications.v1.dependencies import get_email_notification_service
from app.features.notifications.v1.email.service import EmailNotificationService
from app.features.users.v1.dependencies import (
    get_refresh_token_repo,
    get_user_repo,
    get_verification_token_repo,
)
from app.features.users.v1.repository import (
    RefreshTokensRepository,
    UserRepository,
    VerificationTokenRepository,
)


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    verification_token_repo: Annotated[
        VerificationTokenRepository, Depends(get_verification_token_repo)
    ],
    refresh_token_repo: Annotated[
        RefreshTokensRepository, Depends(get_refresh_token_repo)
    ],
    email_notification_service: Annotated[
        EmailNotificationService, Depends(get_email_notification_service)
    ],
) -> AuthService:
    return AuthService(
        session=session,
        user_repo=user_repo,
        verification_token_repo=verification_token_repo,
        refresh_token_repo=refresh_token_repo,
        email_notification_service=email_notification_service,
    )
