import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundException
from app.core.schemas import PaginatedData
from app.features.audits.v1.models import AuditRecord
from app.features.audits.v1.repository import AuditRepository
from app.features.audits.v1.schemas.req import AuditLogFilterParams
from app.features.audits.v1.schemas.res import AuditLogResponse


class AuditService:
    def __init__(
        self,
        session: AsyncSession,
        audits_repo: AuditRepository,
    ):
        self.session = session
        self.audits_repo = audits_repo

    async def get_audit_logs(
        self, filters: AuditLogFilterParams
    ) -> PaginatedData[AuditLogResponse]:
        audit_logs, total_count = await self.audits_repo.get_audit_logs(
            filters.model_dump(exclude_unset=True)
        )
        audit_log_schemas = [AuditLogResponse.model_validate(log) for log in audit_logs]

        paginated_audit_logs = PaginatedData(
            items=audit_log_schemas,
            total=total_count,
            page=filters.page,
            size=filters.size,
        )
        return paginated_audit_logs

    async def get_audit_log(self, audit_log_id: uuid.UUID) -> AuditRecord:
        audit_log = await self.audits_repo.get_audit_log_by_id(audit_log_id)
        if not audit_log:
            raise ResourceNotFoundException()
        return audit_log
