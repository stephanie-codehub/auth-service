from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidRequestException
from app.core.security import hash_password, verify_password
from app.features.users.v1.exceptions import InvalidPasswordException
from app.features.users.v1.models import User
from app.features.users.v1.repository import UserRepository
from app.features.users.v1.schemas.req import ChangePasswordRequest, UpdateUserProfile


class UserService:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
    ):
        self.session = session
        self.user_repo = user_repo

    async def change_user_password(
        self, input_data: ChangePasswordRequest, current_user: User
    ) -> None:
        old_password_valid = verify_password(
            input_data.current_password, current_user.hashed_password
        )
        if not old_password_valid:
            raise InvalidPasswordException()
        current_user.hashed_password = hash_password(input_data.new_password)
        await self.user_repo.save_user_record(current_user)
        await self.session.commit()

    async def update_user_profile(
        self, input_data: UpdateUserProfile, current_user: User
    ) -> User:
        update_data = input_data.model_dump(exclude_unset=True)
        if not update_data:
            raise InvalidRequestException()
        for key, value in update_data.items():
            setattr(current_user, key, value)
        user = await self.user_repo.save_user_record(current_user)
        await self.session.commit()
        return user
