import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundException
from app.core.schemas import PaginatedData
from app.features.admin.v1.schemas.req import UserFilterParams
from app.features.users.v1.models import User
from app.features.users.v1.repository import UserRepository
from app.features.users.v1.schemas.res import UserProfileResponse


class AdminService:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
    ):
        self.session = session
        self.user_repo = user_repo

    async def get_users(
        self, filters: UserFilterParams
    ) -> PaginatedData[UserProfileResponse]:
        users, total_count = await self.user_repo.get_users(
            filters.model_dump(exclude_unset=True)
        )
        user_schemas = [UserProfileResponse.model_validate(user) for user in users]
        paginated_users = PaginatedData(
            items=user_schemas, total=total_count, page=filters.page, size=filters.size
        )
        return paginated_users

    async def get_user_profile_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_user_profile_by_id(user_id)
        if not user:
            raise ResourceNotFoundException()
        return user
