from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_session
from app.features.users.v1.repository import (
    RefreshTokensRepository,
    UserRepository,
    VerificationTokenRepository,
)
from app.features.users.v1.service import UserService


def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return UserRepository(session=session)


def get_verification_token_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> VerificationTokenRepository:
    return VerificationTokenRepository(session=session)


def get_refresh_token_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RefreshTokensRepository:
    return RefreshTokensRepository(session=session)


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserService:
    return UserService(session=session, user_repo=user_repo)
