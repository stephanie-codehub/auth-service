import uuid

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import ColumnElement

from app.features.users.v1.models import RefreshToken, User, VerificationToken
from app.features.users.v1.schemas.enums import VerificationTokenType


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_users(self, filter_dict: dict) -> tuple[list[User], int]:
        query = select(User)
        filter_dict_page = filter_dict["page"]
        filter_dict_size = filter_dict["size"]
        filters: list[ColumnElement[bool]] = []

        if filter_dict.get("email"):
            filters.append(User.email.ilike(f"%{filter_dict['email']}%"))

        if filter_dict.get("first_name"):
            filters.append(User.first_name.ilike(f"%{filter_dict['first_name']}%"))

        if filter_dict.get("last_name"):
            filters.append(User.last_name.ilike(f"%{filter_dict['last_name']}%"))

        if filter_dict.get("phone_number"):
            filters.append(User.phone_number.contains(filter_dict["phone_number"]))

        if "is_active" in filter_dict:
            filters.append(User.is_active == filter_dict["is_active"])

        if filter_dict.get("user_role"):
            filters.append(User.roles.contains(filter_dict["user_role"]))

        if filters:
            query = query.where(and_(*filters))

        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar_one()

        offset_value = (filter_dict_page - 1) * filter_dict_size
        paginated_query = query.offset(offset_value).limit(filter_dict_size)

        result = await self.session.execute(paginated_query)
        users = list(result.scalars().all())

        return users, total_count

    async def get_user_profile_by_id(self, user_id: uuid.UUID) -> User | None:
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def save_user_record(self, user_model: User) -> User:
        self.session.add(user_model)
        await self.session.flush()
        return user_model


class VerificationTokenRepository:
    """Manages User Tokens for Account Verification and Password Reset Validation"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_user_by_token_type(
        self, token: str, token_type: VerificationTokenType
    ) -> User | None:
        statement = (
            select(VerificationToken)
            .where(
                VerificationToken.token == token,
                VerificationToken.token_type == token_type,
            )
            .options(joinedload(VerificationToken.user))
        )
        result = await self.session.execute(statement)
        token_record = result.scalar_one_or_none()

        if token_record:
            return token_record.user
        return None

    async def get_user_by_password_reset_token(self, token: str) -> User | None:
        user = await self._get_user_by_token_type(
            token, VerificationTokenType.PASSWORD_RESET
        )
        return user

    async def get_user_by_activation_token(self, token: str) -> User | None:
        user = await self._get_user_by_token_type(
            token, VerificationTokenType.ACCOUNT_ACTIVATION
        )
        return user

    async def delete_token_by_user_id(self, user_id: uuid.UUID) -> None:
        stmt = delete(VerificationToken).where(VerificationToken.user_id == user_id)
        await self.session.execute(stmt)
        await self.session.flush()


class RefreshTokensRepository:
    """Manages User Refresh Tokens"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_token(
        self,
        token: str,
    ) -> User | None:
        statement = (
            select(RefreshToken)
            .where(
                RefreshToken.token == token,
            )
            .options(joinedload(RefreshToken.user))
        )
        result = await self.session.execute(statement)
        token_record = result.scalar_one_or_none()

        if token_record:
            return token_record.user
        return None

    async def delete_token_by_user_id(self, user_id: uuid.UUID) -> None:
        stmt = delete(RefreshToken).where(RefreshToken.user_id == user_id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def delete_token_by_token(self, token: str) -> None:
        stmt = delete(RefreshToken).where(RefreshToken.token == token)
        await self.session.execute(stmt)
        await self.session.flush()

    async def save_refresh_token(self, token: RefreshToken) -> None:
        self.session.add(token)
        await self.session.flush()
