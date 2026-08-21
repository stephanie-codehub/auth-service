from datetime import UTC, datetime, timedelta

import time_machine
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.core.security import decode_access_token, verify_password
from app.features.users.v1.models import RefreshToken, User
from app.features.users.v1.schemas.enums import VerificationTokenType

SECONDS_IN_A_DAY = 86400
date: datetime = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


class TestUserRegistration:
    endpoint: str = "/auth/register"

    @time_machine.travel(date, tick=False)
    async def test_successful_new_user_registration(
        self, api_client, db_session, mock_email_service
    ):
        input_data = {
            "email": "test@example.com",
            "password": "SecurePassword123",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+2347094785997",
        }
        response = await api_client.post(self.endpoint, json=input_data)

        assert response.status_code == 202

        result = await db_session.execute(
            select(User)
            .where(User.email == input_data["email"])
            .options(joinedload(User.verification_token))
        )
        saved_user = result.scalar_one_or_none()

        assert saved_user is not None
        assert saved_user.is_active is False
        assert saved_user.email == input_data["email"]
        assert saved_user.first_name == input_data["first_name"]
        assert saved_user.last_name == input_data["last_name"]
        assert saved_user.phone_number == input_data["phone_number"]
        assert saved_user.verification_token is not None
        assert (
            verify_password(
                SecretStr(input_data["password"]), saved_user.hashed_password
            )
            is True
        )
        expected_expiration = date + timedelta(
            days=settings.activation_token_expire_days
        )
        assert (
            saved_user.verification_token.token_type
            == VerificationTokenType.ACCOUNT_ACTIVATION
        )
        assert saved_user.verification_token.expires_at == expected_expiration

        mock_email_service.send_account_verification_email.assert_called_once_with(
            input_data["email"],
            f"{settings.api_base_url}/auth/verify?token={saved_user.verification_token.token}",
        )

    @time_machine.travel(date, tick=False)
    async def test_re_registration_of_inactive_user(
        self, api_client, inactive_user, db_session, mock_email_service
    ):
        input_data = {
            "email": inactive_user.email,
            "password": "SecurePassword12345",
            "first_name": "Test",
            "last_name": "New",
            "phone_number": "+2347094785999",
        }

        response = await api_client.post(self.endpoint, json=input_data)

        assert response.status_code == 202

        result = await db_session.execute(
            select(User)
            .where(User.email == input_data["email"])
            .options(joinedload(User.verification_token))
        )
        saved_user = result.scalar_one_or_none()

        assert saved_user is not None
        assert saved_user.id == inactive_user.id
        assert saved_user.is_active is False
        assert saved_user.email == inactive_user.email
        assert saved_user.first_name == input_data["first_name"]
        assert saved_user.last_name == input_data["last_name"]
        assert saved_user.phone_number == input_data["phone_number"]
        assert (
            verify_password(
                SecretStr(input_data["password"]), saved_user.hashed_password
            )
            is True
        )
        assert saved_user.verification_token is not None
        expected_expiration = date + timedelta(
            days=settings.activation_token_expire_days
        )
        assert saved_user.verification_token.expires_at == expected_expiration

        mock_email_service.send_account_verification_email.assert_called_once_with(
            input_data["email"],
            f"{settings.api_base_url}/auth/verify?token={saved_user.verification_token.token}",
        )

    async def test_re_registration_of_active_user(
        self, api_client, db_session, active_user, mock_email_service
    ):
        input_data = {
            "email": active_user.email,
            "password": "SecurePassword1234",
            "first_name": "Test",
            "last_name": "New",
            "phone_number": "+2347094785999",
        }
        response = await api_client.post(self.endpoint, json=input_data)

        assert response.status_code == 202

        result = await db_session.execute(
            select(User).where(User.email == input_data["email"])
        )
        saved_user = result.scalar_one_or_none()

        assert saved_user is not None
        assert saved_user.id == active_user.id
        assert saved_user.is_active is True
        assert saved_user.email == active_user.email
        assert saved_user.first_name == active_user.first_name
        assert saved_user.last_name == active_user.last_name
        assert saved_user.phone_number == active_user.phone_number
        assert (
            verify_password(
                SecretStr(input_data["password"]), saved_user.hashed_password
            )
            is False
        )
        mock_email_service.send_account_verification_email.assert_not_called()
        mock_email_service.send_already_registered_email.assert_called_once_with(
            input_data["email"]
        )


class TestUserLogin:
    endpoint: str = "/auth/login"

    @time_machine.travel(date, tick=False)
    async def test_correct_credentials(self, api_client, db_session, active_user):
        input_data = {"email": "active@example.com", "password": "SecurePassword123"}
        response = await api_client.post(self.endpoint, json=input_data)

        assert response.status_code == 200
        assert "refresh_token" in response.cookies
        """cookie = api_client.cookies.get_dict_attrs("refresh_token")
        assert cookie.get("httponly") is True
        assert cookie.get("secure") is True
        assert cookie.get("samesite") == "Lax"
        assert cookie.get("path") == "/auth/token/refresh"
        expected_max_age = str(settings.refresh_token_expire_days * SECONDS_IN_A_DAY)
        assert cookie.get("expires") == expected_max_age"""

        data = response.json()
        access_token = data["data"]["access_token"]

        assert access_token is not None
        assert decode_access_token(access_token) is not None

        result = await db_session.execute(
            select(RefreshToken).where(RefreshToken.user_id == active_user.id)
        )
        refresh_token = result.scalar_one_or_none()
        assert refresh_token.expires_at == date + timedelta(
            days=settings.refresh_token_expire_days
        )

    async def test_wrong_password(self): ...
    async def test_invalid_account(self): ...
    async def test_unverified_account(self): ...


"""
async def test_get_protected_profile_endpoint(auth_client, test_user):
    response = await auth_client.get("/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == str(test_user.id)


async def test_unauthenticated_request_fails(db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/users/me")

    assert response.status_code == 401
    app.dependency_overrides.clear()
"""
