import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import InvalidAuthTokenException
from app.core.security import create_access_token, hash_password, verify_password
from app.features.auth.v1.exceptions import (
    InvalidAccountTokenException,
    InvalidCredentialsError,
    UnverifiedAccountException,
)
from app.features.auth.v1.schemas.req import (
    CompletePasswordReset,
    InitiatePasswordReset,
    UserLogin,
    UserRegister,
)
from app.features.auth.v1.schemas.res import TokenResponse
from app.features.notifications.v1.email.service import EmailNotificationService
from app.features.users.v1.models import (
    RefreshToken,
    User,
    UserRoleTable,
    VerificationToken,
)
from app.features.users.v1.repository import (
    RefreshTokensRepository,
    UserRepository,
    VerificationTokenRepository,
)
from app.features.users.v1.schemas.enums import UserRole, VerificationTokenType


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        verification_token_repo: VerificationTokenRepository,
        refresh_token_repo: RefreshTokensRepository,
        email_notification_service: EmailNotificationService,
    ):
        self.session = session
        self.user_repo = user_repo
        self.verification_token_repo = verification_token_repo
        self.refresh_token_repo = refresh_token_repo
        self.email_notification_service = email_notification_service

    async def register_user(self, input_data: UserRegister) -> None:
        user = await self.user_repo.get_user_by_email(input_data.email)

        if user and user.is_active:
            self.email_notification_service.send_already_registered_email(user.email)
            return  # For account enumeration attacks, no exception is raised

        input_data_dict = input_data.model_dump(exclude={"password"})

        # If an inactive user exists, update data
        if user:
            for key, value in input_data_dict.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            await self.verification_token_repo.delete_token_by_user_id(user.id)
        else:
            user = User(**input_data_dict)
            user.roles = [UserRoleTable(user_role=UserRole.USER)]
        hashed_password = hash_password(input_data.password)
        user.hashed_password = hashed_password
        user.is_active = False
        token_str = secrets.token_urlsafe(32)
        token = VerificationToken(
            token=token_str,
            token_type=VerificationTokenType.ACCOUNT_ACTIVATION,
            expires_at=datetime.now(UTC)
            + timedelta(days=settings.activation_token_expire_days),
        )
        user.verification_token = token
        saved_user = await self.user_repo.save_user_record(user)
        await self.session.commit()

        verification_url = f"{settings.api_base_url}/auth/verify?token={token_str}"
        self.email_notification_service.send_account_verification_email(
            saved_user.email, verification_url
        )

    async def generate_new_auth_token_pair(
        self, user_id: uuid.UUID, user_roles: list[UserRole]
    ) -> TokenResponse:
        access_token = create_access_token(user_id, user_roles)
        refresh_token_str = secrets.token_urlsafe(32)
        await self.refresh_token_repo.delete_token_by_user_id(user_id)  # TO DO
        refresh_token = RefreshToken(
            user_id=user_id,
            token=refresh_token_str,
            expires_at=datetime.now(UTC)
            + timedelta(days=settings.refresh_token_expire_days),
        )
        await self.refresh_token_repo.save_refresh_token(refresh_token)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token_str)

    async def login_user(self, input_data: UserLogin) -> TokenResponse:
        user = await self.user_repo.get_user_by_email(input_data.email)

        if not user or not verify_password(input_data.password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise UnverifiedAccountException()

        auth_tokens = await self.generate_new_auth_token_pair(
            user.id, [role.user_role for role in user.roles]
        )
        user.last_login = datetime.now(UTC)
        await self.user_repo.save_user_record(user)
        await self.session.commit()
        return auth_tokens

    async def activate_user_account(self, token: str) -> None:
        user = await self.verification_token_repo.get_user_by_activation_token(token)

        if (
            not user
            or not user.verification_token
            or (datetime.now(UTC) > user.verification_token.expires_at)
        ):
            raise InvalidAccountTokenException()

        user.is_active = True
        await self.verification_token_repo.delete_token_by_user_id(user.id)
        await self.user_repo.save_user_record(user)
        await self.session.commit()

    async def refresh_token(self, token: str | None) -> TokenResponse:
        if not token:
            raise InvalidAuthTokenException()

        user = await self.refresh_token_repo.get_user_by_token(token)

        if (
            not user
            or not user.refresh_token
            or (datetime.now(UTC) > user.refresh_token.expires_at)
        ):
            raise InvalidAuthTokenException()

        if not user.is_active:
            raise UnverifiedAccountException()

        auth_tokens = await self.generate_new_auth_token_pair(
            user.id, [role.user_role for role in user.roles]
        )
        await self.session.commit()
        return auth_tokens

    async def logout(self, token: str | None):
        if token:
            await self.refresh_token_repo.delete_token_by_token(token)
            await self.session.commit()

    async def initiate_password_reset(
        self,
        input_data: InitiatePasswordReset,
    ):
        user = await self.user_repo.get_user_by_email(input_data.email)

        if not user:
            return  # For account enumeration attacks

        token = VerificationToken(
            token=secrets.token_urlsafe(32),
            token_type=VerificationTokenType.PASSWORD_RESET,
            expires_at=datetime.now(UTC)
            + timedelta(days=settings.password_reset_token_expire_hours),
        )
        user.verification_token = token
        saved_user = await self.user_repo.save_user_record(user)
        await self.session.commit()

        verification_url = (
            f"{settings.api_base_url}/auth/reset-password-form?token={token.token}"
        )
        self.email_notification_service.send_password_reset_email(
            saved_user.email, verification_url
        )

    async def complete_password_reset(
        self,
        input_data: CompletePasswordReset,
    ):
        user = await self.verification_token_repo.get_user_by_password_reset_token(
            input_data.token
        )

        if (
            not user
            or not user.verification_token
            or (datetime.now(UTC) > user.verification_token.expires_at)
        ):
            raise InvalidAccountTokenException()

        user.hashed_password = hash_password(input_data.new_password)
        await self.verification_token_repo.delete_token_by_user_id(user.id)
        await self.user_repo.save_user_record(user)
        await self.session.commit()
