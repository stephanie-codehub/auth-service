import uuid

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.audits.v1.models import AuditRecord


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_audit_logs(self, filter_dict: dict) -> tuple[list[AuditRecord], int]:
        query = select(AuditRecord)
        filter_dict_page = filter_dict["page"]
        filter_dict_size = filter_dict["size"]
        filters = []

        if filter_dict.get("activity_type"):
            filters.append(
                AuditRecord.activity_type.ilike(f"%{filter_dict['activity_type']}%")
            )

        if filter_dict.get("activity_status"):
            filters.append(
                AuditRecord.activity_status.ilike(f"%{filter_dict['activity_status']}%")
            )

        if filter_dict.get("device_type"):
            filters.append(
                AuditRecord.device_type.ilike(f"%{filter_dict['device_type']}%")
            )

        if filter_dict.get("device_name"):
            filters.append(AuditRecord.device_name.contains(filter_dict["device_name"]))

        if filter_dict.get("location"):
            filters.append(AuditRecord.location.contains(filter_dict["location"]))

        if filter_dict.get("ip_address"):
            filters.append(AuditRecord.ip_address == filter_dict["ip_address"])

        if filter_dict.get("audit_log_id"):
            filters.append(AuditRecord.audit_log_id == filter_dict["audit_log_id"])

        if filter_dict.get("timestamp"):
            filters.append(AuditRecord.timestamp == filter_dict["timestamp"])

        if filters:
            query = query.where(and_(*filters))

        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar_one()

        offset_value = (filter_dict_page - 1) * filter_dict_size
        paginated_query = query.offset(offset_value).limit(filter_dict_size)

        result = await self.session.execute(paginated_query)
        audit_logs = list(result.scalars().all())

        return audit_logs, total_count

    async def get_audit_log_by_id(self, audit_log_id: uuid.UUID) -> AuditRecord | None:
        statement = select(AuditRecord).where(AuditRecord.id == audit_log_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def save_audit_log_record(self, audit_log_model: AuditRecord) -> AuditRecord:
        self.session.add(audit_log_model)
        await self.session.flush()
        return audit_log_model
