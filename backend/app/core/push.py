"""
core/push.py
Thin FCM sender using the HTTP v1 API via httpx.

If FCM_SERVER_KEY is not configured, push is silently skipped so the app
works without Firebase credentials during local development.

Phase 1: send to all registered device tokens for the user.
"""
import logging
from typing import Optional
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.notification import Device

logger = logging.getLogger(__name__)

# Legacy FCM endpoint (works with server key, no service-account JSON needed for Phase 1)
FCM_URL = "https://fcm.googleapis.com/fcm/send"


async def send_fcm_push(
    db: AsyncSession,
    user_id: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> None:
    """
    Send an FCM push notification to every device token the user has registered.
    Silently no-ops when FCM_SERVER_KEY is absent (local dev).
    Removes stale tokens (404 / invalid-registration responses from FCM).
    """
    if not settings.FCM_SERVER_KEY:
        # No credentials configured — skip push, notification row is already saved
        return

    stmt = select(Device).where(Device.user_id == user_id)
    devices = (await db.execute(stmt)).scalars().all()
    if not devices:
        return

    payload = {
        "notification": {"title": title, "body": body},
        "data": {str(k): str(v) for k, v in (data or {}).items()},
    }
    headers = {
        "Authorization": f"key={settings.FCM_SERVER_KEY}",
        "Content-Type": "application/json",
    }

    stale_tokens = []
    async with httpx.AsyncClient(timeout=10) as client:
        for device in devices:
            try:
                resp = await client.post(
                    FCM_URL,
                    headers=headers,
                    json={**payload, "to": device.fcm_token},
                )
                result = resp.json()
                # FCM returns results[0].error for per-token errors
                if result.get("failure") and result.get("results"):
                    err = result["results"][0].get("error", "")
                    if err in ("InvalidRegistration", "NotRegistered"):
                        stale_tokens.append(device.fcm_token)
            except Exception as exc:
                logger.warning("FCM push failed for token %s: %s", device.fcm_token[:20], exc)

    # Clean up stale tokens
    for token in stale_tokens:
        stmt = select(Device).where(Device.fcm_token == token)
        dev = (await db.execute(stmt)).scalar_one_or_none()
        if dev:
            await db.delete(dev)
    if stale_tokens:
        await db.commit()
