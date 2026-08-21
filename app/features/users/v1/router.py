from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.core.schemas import ApiResponse
from app.features.users.v1.dependencies import get_user_service
from app.features.users.v1.models import User
from app.features.users.v1.schemas.req import ChangePasswordRequest, UpdateUserProfile
from app.features.users.v1.schemas.res import UserProfileResponse
from app.features.users.v1.service import UserService

user_router = APIRouter()


@user_router.get("/profile", response_model=ApiResponse[UserProfileResponse])
async def get_my_profile(current_user: Annotated[User, Depends(get_current_user)]):
    return ApiResponse(data=current_user)


@user_router.patch("/profile", response_model=ApiResponse[UserProfileResponse])
async def update_user_profile(
    input_data: UpdateUserProfile,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    user = await service.update_user_profile(input_data, current_user)
    return ApiResponse(message="Profile updated successfully.", data=user)


@user_router.post("/profile/change-password", response_model=ApiResponse)
async def change_user_password(
    input_data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    await service.change_user_password(input_data, current_user)
    return ApiResponse(message="Account password updated successfully")
