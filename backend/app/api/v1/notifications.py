from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.notification import Notification, NotificationPref, Device
from app.schemas.notification import (
    NotificationRead,
    NotificationPrefRead,
    NotificationPrefUpdate,
    DeviceRegister,
)

router = APIRouter(tags=["Notifications"])


async def dispatch_notification(
    db: AsyncSession,
    user_id: str,
    topic: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> Optional[Notification]:
    """
    Enforces Phase 1 Notification Rules:
    - Per-topic mute
    - Quiet hours
    - Daily push cap (default: 3 pushes per user per day)
    """
    # Fetch or create user preferences
    pref_stmt = select(NotificationPref).where(NotificationPref.user_id == user_id)
    pref = (await db.execute(pref_stmt)).scalar_one_or_none()
    if not pref:
        pref = NotificationPref(
            user_id=user_id,
            muted_topics=[],
            daily_count=0,
            last_count_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        )
        db.add(pref)
        await db.commit()
        await db.refresh(pref)

    # 1. Check topic mute
    if topic in (pref.muted_topics or []):
        return None

    # 2. Check quiet hours
    now_hour = datetime.now(timezone.utc).hour
    if pref.quiet_hours_start is not None and pref.quiet_hours_end is not None:
        if pref.quiet_hours_start <= pref.quiet_hours_end:
            in_quiet = pref.quiet_hours_start <= now_hour < pref.quiet_hours_end
        else:
            in_quiet = now_hour >= pref.quiet_hours_start or now_hour < pref.quiet_hours_end
        if in_quiet:
            return None

    # 3. Check and reset daily push cap
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if pref.last_count_date != today_str:
        pref.daily_count = 0
        pref.last_count_date = today_str

    if pref.daily_count >= settings.MAX_PUSH_NOTIFICATIONS_PER_DAY:
        # Cap reached: do not send push
        return None

    pref.daily_count += 1

    notif = Notification(
        user_id=user_id,
        topic=topic,
        title=title,
        body=body,
        data=data or {},
        is_read=False,
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return notif


@router.get("/notifications", response_model=List[NotificationRead], summary="Get notifications for current user")
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    res = await db.execute(stmt)
    return res.scalars().all()


@router.patch("/notifications/{notification_id}/read", response_model=NotificationRead, summary="Mark notification as read")
async def mark_notification_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    )
    res = await db.execute(stmt)
    notif = res.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notif.is_read = True
    await db.commit()
    await db.refresh(notif)
    return notif


@router.get("/me/notification-prefs", response_model=NotificationPrefRead, summary="Get notification preferences")
async def get_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(NotificationPref).where(NotificationPref.user_id == current_user.id)
    pref = (await db.execute(stmt)).scalar_one_or_none()
    if not pref:
        pref = NotificationPref(
            user_id=current_user.id,
            muted_topics=[],
            daily_count=0,
            last_count_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        )
        db.add(pref)
        await db.commit()
        await db.refresh(pref)
    return pref


@router.put("/me/notification-prefs", response_model=NotificationPrefRead, summary="Update notification preferences")
async def update_preferences(
    payload: NotificationPrefUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(NotificationPref).where(NotificationPref.user_id == current_user.id)
    pref = (await db.execute(stmt)).scalar_one_or_none()
    if not pref:
        pref = NotificationPref(user_id=current_user.id)
        db.add(pref)

    if payload.muted_topics is not None:
        pref.muted_topics = payload.muted_topics
    if payload.quiet_hours_start is not None:
        pref.quiet_hours_start = payload.quiet_hours_start
    if payload.quiet_hours_end is not None:
        pref.quiet_hours_end = payload.quiet_hours_end

    await db.commit()
    await db.refresh(pref)
    return pref


@router.post("/devices", summary="Register device for push notifications")
async def register_device(
    payload: DeviceRegister,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Device).where(Device.fcm_token == payload.fcm_token)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        existing.user_id = current_user.id
        existing.device_type = payload.device_type
    else:
        new_device = Device(
            user_id=current_user.id,
            fcm_token=payload.fcm_token,
            device_type=payload.device_type,
        )
        db.add(new_device)

    await db.commit()
    return {"message": "Device registered successfully"}
