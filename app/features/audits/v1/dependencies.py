from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_session
from app.features.audits.v1.repository import AuditRepository
from app.features.audits.v1.service import AuditService


def get_audit_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuditRepository:
    return AuditRepository(session=session)


def get_audit_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    audit_repo: Annotated[AuditRepository, Depends(get_audit_repo)],
) -> AuditService:
    return AuditService(
        session=session,
        audits_repo=audit_repo,
    )
