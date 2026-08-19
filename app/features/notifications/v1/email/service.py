import resend
import structlog
from fastapi import BackgroundTasks

from app.core.config import settings
from app.core.utils import render_email_template
from app.features.notifications.v1.email.schemas.enums import EmailTemplateType
from app.features.notifications.v1.email.schemas.req import EmailNotificationRequest

logger = structlog.getLogger()

resend.api_key = settings.resend_api_key.get_secret_value()


async def _send_email_task(to: str, subject: str, html_content: str):
    try:
        await resend.Emails.send_async(
            {
                "from": settings.sender_email,
                "to": to,
                "subject": subject,
                "html": html_content,
            }
        )
    except Exception:
        logger.exception("Error sending email")


class EmailNotificationService:
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    def _queue_email(
        self,
        to: str,
        subject: str,
        template_name: str,
        template_vars: dict | None = None,
    ):
        html = render_email_template(template_name, template_vars)
        self.background_tasks.add_task(
            _send_email_task, to=to, subject=subject, html_content=html
        )

    def send_account_verification_email(
        self, user_email: str, email_confirmation_link: str
    ):
        self._queue_email(
            to=user_email,
            subject="Verify Your Account",
            template_name="account_verification.html",
            template_vars={"email_confirmation_link": email_confirmation_link},
        )

    def send_password_reset_email(self, user_email: str, password_reset_link: str):
        self._queue_email(
            to=user_email,
            subject="Password Reset Request",
            template_name="password_reset.html",
            template_vars={"password_reset_link": password_reset_link},
        )

    def send_password_reset_confirmation_email(self, user_email: str):
        self._queue_email(
            to=user_email,
            subject="Password Change Confirmation",
            template_name="password_reset_confirmation.html",
        )

    def send_already_registered_email(self, user_email: str):
        self._queue_email(
            to=user_email,
            subject="You already have an account",
            template_name="user_already_registered.html",
        )

    def send_otp_email(self, email: str, code: str):
        self._queue_email(
            to=email,
            subject="One-Time Password",
            template_name="otp.html",
            template_vars={"otp_code": code},
        )

    def send_email_notification(self, input_data: EmailNotificationRequest):
        match input_data.template_type:
            case EmailTemplateType.ACCOUNT_VERIFICATION:
                self.send_account_verification_email(
                    input_data.to_address, "https://google.com"
                )
            case EmailTemplateType.PASSWORD_RESET:
                self.send_password_reset_email(
                    input_data.to_address, "https://google.com"
                )
            case EmailTemplateType.PASSWORD_RESET_CONFIRMATION:
                self.send_password_reset_confirmation_email(input_data.to_address)
            case EmailTemplateType.OTP:
                self.send_otp_email(input_data.to_address, "5784")
