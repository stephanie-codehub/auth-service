import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.schemas import ApiResponse, PaginatedData
from app.features.audits.v1.dependencies import get_audit_service
from app.features.audits.v1.schemas.req import AuditLogFilterParams
from app.features.audits.v1.schemas.res import AuditLogResponse
from app.features.audits.v1.service import AuditService

audit_router = APIRouter()


@audit_router.get("/", response_model=ApiResponse[PaginatedData[AuditLogResponse]])
async def get_audit_logs(
    filters: Annotated[AuditLogFilterParams, Query()],
    service: Annotated[
        AuditService,
        Depends(get_audit_service),
    ],
):
    paginated_audit_logs = await service.get_audit_logs(filters)
    return ApiResponse(data=paginated_audit_logs)


@audit_router.get(
    "/audit_logs/{audit_log_id}", response_model=ApiResponse[AuditLogResponse]
)
async def get_audit_log_profile(
    audit_log_id: uuid.UUID,
    service: Annotated[
        AuditService,
        Depends(get_audit_service),
    ],
):
    audit_log = await service.get_audit_log(audit_log_id)
    return ApiResponse(data=audit_log)
