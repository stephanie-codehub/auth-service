from unittest.mock import MagicMock

import pytest
from fastapi import BackgroundTasks
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database.session import Base, get_session
from app.core.security import create_access_token, hash_password
from app.features.auth.v1.service import AuthService
from app.features.notifications.v1.dependencies import get_email_notification_service
from app.features.users.v1.dependencies import (
    get_refresh_token_repo,
    get_user_repo,
    get_verification_token_repo,
)
from app.features.users.v1.models import (
    User,
    UserRoleTable,
)
from app.features.users.v1.schemas.enums import UserRole
from app.main import app

test_engine = create_async_engine(settings.test_database_url)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.connect() as connection:
        await connection.execute(text("DROP SCHEMA public CASCADE;"))
        await connection.execute(text("CREATE SCHEMA public;"))
        await connection.commit()


@pytest.fixture(scope="function")
async def db_session():
    async with test_engine.connect() as connection, connection.begin() as transaction:
        async with TestSessionLocal(bind=connection) as session:
            yield session
        await transaction.rollback()


@pytest.fixture
def mock_email_service():
    service = MagicMock()
    service.send_account_verification_email = MagicMock()
    service.send_already_registered_email = MagicMock()
    return service


@pytest.fixture
def auth_service(mock_email_service, db_session):
    return AuthService(
        user_repo=get_user_repo(session=db_session),
        verification_token_repo=get_verification_token_repo(session=db_session),
        refresh_token_repo=get_refresh_token_repo(session=db_session),
        email_notification_service=mock_email_service,
        session=db_session,
    )


@pytest.fixture
async def api_client(db_session, mock_email_service):
    app.dependency_overrides[get_session] = lambda: db_session

    def override_email_service(background_tasks: BackgroundTasks):
        return mock_email_service

    app.dependency_overrides[get_email_notification_service] = override_email_service

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost/api/v1"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def active_user(db_session):
    user = User(
        email="active@example.com",
        first_name="active",
        last_name="User",
        hashed_password=hash_password("SecurePassword123"),
        roles=[UserRoleTable(user_role=UserRole.USER)],
        phone_number="+2347094989997",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def inactive_user(db_session):
    user = User(
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        hashed_password=hash_password("SecurePassword123"),
        roles=[UserRoleTable(user_role=UserRole.USER)],
        phone_number="+2347094989997",
        is_active=False,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def test_admin(db_session):
    user = User(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        roles=[
            UserRoleTable(user_role=UserRole.USER),
            UserRoleTable(user_role=UserRole.ADMIN),
        ],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def auth_client(db_session, active_user):
    app.dependency_overrides[get_session] = lambda: db_session
    token = create_access_token(active_user.id, active_user.roles)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost/api/v1",
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        yield client

    app.dependency_overrides.clear()
