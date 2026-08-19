import uuid
from datetime import UTC, datetime

import structlog
from fastapi import BackgroundTasks, FastAPI, Request

from app.core.database.session import AsyncSessionLocal
from app.core.utils import get_client_ip
from app.features.audits.v1.models import AuditRecord
from app.features.audits.v1.schemas.enums import ActivityStatus

logger = structlog.get_logger()


def extract_device_info(request: Request) -> tuple[str, str]:
    """
    Parses the User-Agent header to extract device info
    """
    user_agent = request.headers.get("user-agent", "").lower()
    if not user_agent:
        return "Unknown", "Unknown"

    if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
        device_type = "Mobile"
    elif "tablet" in user_agent or "ipad" in user_agent:
        device_type = "Tablet"
    elif "bot" in user_agent or "spider" in user_agent or "crawler" in user_agent:
        device_type = "Bot/Crawler"
    else:
        device_type = "Desktop"

    if "iphone" in user_agent:
        device_name = "iPhone"
    elif "ipad" in user_agent:
        device_name = "iPad"
    elif "android" in user_agent:
        device_name = "Android Device"
    elif "windows" in user_agent:
        device_name = "Windows PC"
    elif "macintosh" in user_agent:
        device_name = "Mac"
    elif "linux" in user_agent:
        device_name = "Linux PC"
    else:
        device_name = "Generic Browser"

    return device_type, device_name


async def extract_location(ip_address: str) -> str:
    """
    Extracts geographic location from IP address
    """

    return "Unknown Location"


async def save_audit_log(
    user_id: uuid.UUID,
    activity_type: str,
    activity_status: str,
    ip_address: str,
    device_type: str,
    device_name: str,
    timestamp: datetime,
) -> None:
    location = await extract_location(ip_address)
    async with AsyncSessionLocal() as session:
        try:
            audit_entry = AuditRecord(
                activity_type=activity_type,
                activity_status=activity_status,
                device_type=device_type,
                device_name=device_name,
                location=location,
                ip_address=ip_address,
                user_id=user_id,
                timestamp=timestamp,
            )

            session.add(audit_entry)
            await session.commit()
            logger.info(
                f"Audit trace recorded successfully to DB: {activity_type} [{activity_status}]"
            )

        except Exception:
            await session.rollback()
            logger.exception("Critical: Background audit database save failed")


def register_audit_log_middleware(app: FastAPI):
    @app.middleware("http")
    async def save_audits(request: Request, call_next):
        activity_status = ActivityStatus.SUCCESS
        client_ip = get_client_ip(request)
        device_type, device_name = extract_device_info(request)
        response = await call_next(request)

        timestamp = datetime.now(UTC)
        if response.status_code == 429:
            activity_status = ActivityStatus.RATE_LIMITED
        elif response.status_code >= 400:
            activity_status = ActivityStatus.FAILED

        activity_type = getattr(request.state, "activity_type", None)
        user_id = getattr(request.state, "user_id", None)

        if activity_type:
            if response.background is None:
                response.background = BackgroundTasks()

            response.background.add_task(
                save_audit_log,
                user_id=user_id,
                activity_type=activity_type,
                activity_status=activity_status,
                ip_address=client_ip,
                device_type=device_type,
                device_name=device_name,
                timestamp=timestamp,
            )

        return response
