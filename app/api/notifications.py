from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.models.product import Product
from app.schemas.notification import NotificationOut
from app.auth import get_current_user_optional

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationOut])
async def list_notifications(
    limit: int = Query(20, ge=1, le=50),
    user: Optional[User] = Depends(get_current_user_optional),
    email: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Notification).options(selectinload(Notification.product)).order_by(desc(Notification.created_at))

    if user:
        query = query.where(
            (Notification.user_id == user.id) | (Notification.email == user.email)
        )
    elif email:
        query = query.where(Notification.email == email.strip().lower())
    else:
        # Return recent public notifications / sample demo notifications
        query = query.limit(limit)

    res = await db.execute(query)
    notifs = res.scalars().all()

    results = []
    for n in notifs:
        item = NotificationOut(
            id=n.id,
            user_id=n.user_id,
            email=n.email,
            product_id=n.product_id,
            alert_id=n.alert_id,
            title=n.title,
            message=n.message,
            old_price=n.old_price,
            new_price=n.new_price,
            store_name=n.store_name,
            product_url=n.product_url,
            currency=n.currency,
            is_read=n.is_read,
            created_at=n.created_at,
            product_name=n.product.name if n.product else None,
            product_image=n.product.image_url if n.product else None
        )
        results.append(item)

    return results[:limit]

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db)
):
    notif = await db.get(Notification, notification_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    await db.commit()
    return {"message": "Notification marked as read", "id": notification_id}

@router.post("/read-all")
async def mark_all_notifications_read(
    user: Optional[User] = Depends(get_current_user_optional),
    email: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    if user:
        await db.execute(
            update(Notification)
            .where((Notification.user_id == user.id) | (Notification.email == user.email))
            .values(is_read=True)
        )
    elif email:
        await db.execute(
            update(Notification)
            .where(Notification.email == email.strip().lower())
            .values(is_read=True)
        )
    else:
        await db.execute(update(Notification).values(is_read=True))

    await db.commit()
    return {"message": "All notifications marked as read"}
