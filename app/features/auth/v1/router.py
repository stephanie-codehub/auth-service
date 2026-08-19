from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response, status
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.schemas import ApiResponse
from app.features.auth.v1.dependencies import get_auth_service
from app.features.auth.v1.schemas.req import (
    CompletePasswordReset,
    InitiatePasswordReset,
    UserLogin,
    UserRegister,
)
from app.features.auth.v1.schemas.res import TokenResponse
from app.features.auth.v1.service import AuthService

auth_router = APIRouter()

SECONDS_IN_A_DAY = 86400


@auth_router.post(
    "/register", response_model=ApiResponse, status_code=status.HTTP_202_ACCEPTED
)
async def register(
    input_data: UserRegister, service: Annotated[AuthService, Depends(get_auth_service)]
):
    await service.register_user(input_data)
    return ApiResponse(
        message="A verification email has been sent to the provided email address to complete the account creation process "
    )


@auth_router.post("/verify", response_class=HTMLResponse)
async def activate_user_account(
    token: str, service: Annotated[AuthService, Depends(get_auth_service)]
):
    await service.activate_user_account(token)
    return HTMLResponse("account_activated.html")


@auth_router.post("/login", response_model=ApiResponse[TokenResponse])
async def login_user(
    response: Response,
    input_data: UserLogin,
    service: Annotated[
        AuthService,
        Depends(get_auth_service),
    ],
):
    tokens = await service.login_user(input_data)

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/auth/token/refresh",
        max_age=settings.refresh_token_expire_days * SECONDS_IN_A_DAY,
    )
    return ApiResponse(data=tokens)


@auth_router.post("/token/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_token(
    response: Response,
    service: Annotated[
        AuthService,
        Depends(get_auth_service),
    ],
    refresh_token: str | None = Cookie(default=None),
):
    tokens = await service.refresh_token(refresh_token)
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/auth/token/refresh",
        max_age=settings.refresh_token_expire_days * SECONDS_IN_A_DAY,
    )
    return ApiResponse(data=tokens)


@auth_router.post("/logout", response_model=ApiResponse)
async def logout(
    response: Response,
    service: Annotated[
        AuthService,
        Depends(get_auth_service),
    ],
    refresh_token: str | None = Cookie(default=None),
):
    await service.logout(refresh_token)
    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/auth/token/refresh",
        max_age=0,
    )

    return ApiResponse()


@auth_router.post(
    "/forgot-password", response_model=ApiResponse, status_code=status.HTTP_202_ACCEPTED
)
async def initiate_password_reset(
    input_data: InitiatePasswordReset,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    await service.initiate_password_reset(input_data)
    return ApiResponse(
        message="A password reset link has been sent to the provided email address if an associated account exists"
    )


@auth_router.post("/reset-password", response_class=HTMLResponse)
async def complete_password_reset(
    input_data: CompletePasswordReset,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    await service.complete_password_reset(input_data)
    return HTMLResponse("password_reset.html")
