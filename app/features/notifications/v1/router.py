from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.schemas import ApiResponse
from app.features.notifications.v1.dependencies import get_email_notification_service
from app.features.notifications.v1.email.schemas.req import EmailNotificationRequest
from app.features.notifications.v1.email.service import EmailNotificationService

notification_router = APIRouter()


@notification_router.post(
    "/email/send", response_model=ApiResponse, status_code=status.HTTP_202_ACCEPTED
)
def send_email_notification(
    input_data: EmailNotificationRequest,
    service: Annotated[
        EmailNotificationService, Depends(get_email_notification_service)
    ],
):
    service.send_email_notification(input_data)
    return ApiResponse()


"""
@notification_router.post(
    "/sms/send", response_model=ApiResponse, status_code=status.HTTP_202_ACCEPTED
)
async def send_sms_notification(
    input_data: SmsNotificationRequest,
    service: SmsNotificationService = Depends(get_sms_notification_service),
):
    await service.send_sms_notification(input_data)
    return ApiResponse()
"""
