import uuid
from datetime import datetime

import uuid6
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import AuditRecord
from app.core.database.session import Base
from app.features.users.v1.schemas.enums import UserRole, VerificationTokenType


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid6.uuid7)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(30))
    is_active: Mapped[bool] = mapped_column(default=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    roles: Mapped[list["UserRoleTable"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    verification_token: Mapped["VerificationToken|None"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    refresh_token: Mapped["RefreshToken|None"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    audit_records: Mapped[list["AuditRecord"]] = relationship(back_populates="user")


class UserRoleTable(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_role", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_role: Mapped[UserRole] = mapped_column(
        String(50),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    user: Mapped["User"] = relationship(back_populates="roles")


class VerificationToken(Base):
    __tablename__ = "verification_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(255), unique=True)
    token_type: Mapped[VerificationTokenType] = mapped_column(
        String(50), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )

    user: Mapped["User"] = relationship(back_populates="verification_token")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(255), unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="refresh_token")
