from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_session
from app.features.admin.v1.service import AdminService
from app.features.users.v1.dependencies import get_user_repo
from app.features.users.v1.repository import UserRepository


def get_admin_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> AdminService:
    return AdminService(
        session=session,
        user_repo=user_repo,
    )
