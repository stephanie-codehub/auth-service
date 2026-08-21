from fastapi import APIRouter, Depends

from app.core.dependencies import require_admin_role, require_auth
from app.features.admin.v1.router import admin_router
from app.features.audits.v1.router import audit_router
from app.features.auth.v1.router import auth_router
from app.features.notifications.v1.router import notification_router
from app.features.users.v1.router import user_router

v1_router = APIRouter()
auth_wrapper = APIRouter(dependencies=[Depends(require_auth)])
admin_wrapper = APIRouter(dependencies=[Depends(require_admin_role)])

# PUBLIC ROUTES
v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

#  AUTHENTICATED ROUTES
auth_wrapper.include_router(
    user_router, prefix="/users", tags=["User Account Management"]
)

# AUTHENTICATED ADMIN ROUTES
admin_wrapper.include_router(
    audit_router, prefix="/audit_logs", tags=["System Audit Logs"]
)
admin_wrapper.include_router(admin_router, prefix="/admin", tags=["Admin"])
admin_wrapper.include_router(
    notification_router, prefix="/notifications", tags=["Notifications"]
)

v1_router.include_router(auth_wrapper)
v1_router.include_router(admin_wrapper)
