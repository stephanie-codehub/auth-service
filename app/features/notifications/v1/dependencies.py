from fastapi import BackgroundTasks

from .email.service import EmailNotificationService


def get_email_notification_service(
    background_tasks: BackgroundTasks,
) -> EmailNotificationService:
    return EmailNotificationService(background_tasks=background_tasks)
