import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.schemas import ApiResponse, PaginatedData
from app.features.admin.v1.dependencies import get_admin_service
from app.features.admin.v1.schemas.req import UserFilterParams
from app.features.admin.v1.service import AdminService
from app.features.users.v1.schemas.res import UserProfileResponse

admin_router = APIRouter()


@admin_router.get(
    "/users", response_model=ApiResponse[PaginatedData[UserProfileResponse]]
)
async def get_users(
    filters: Annotated[UserFilterParams, Query()],
    service: Annotated[
        AdminService,
        Depends(get_admin_service),
    ],
):
    paginated_users = await service.get_users(filters)
    return ApiResponse(data=paginated_users)


@admin_router.get("/users/{user_id}", response_model=ApiResponse[UserProfileResponse])
async def get_user_profile(
    user_id: uuid.UUID,
    service: Annotated[
        AdminService,
        Depends(get_admin_service),
    ],
):
    user = await service.get_user_profile_by_id(user_id)
    return ApiResponse(data=user)
