import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import uuid6
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.session import Base
from app.features.audits.v1.schemas.enums import ActivityStatus, ActivityType

if TYPE_CHECKING:
    from app.features.users.v1.models import User


class AuditRecord(Base):
    __tablename__ = "audit_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid6.uuid7)
    activity_type: Mapped[ActivityType] = mapped_column(String(50), nullable=False)
    activity_status: Mapped[ActivityStatus] = mapped_column(String(50), nullable=False)
    device_type: Mapped[str] = mapped_column(
        String(255),
    )
    device_name: Mapped[str] = mapped_column(
        String(255),
    )
    location: Mapped[str] = mapped_column(
        String(255),
    )
    ip_address: Mapped[str] = mapped_column(
        String(255),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user: Mapped["User"] = relationship(back_populates="audit_records")
