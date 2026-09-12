from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.alert import PriceAlert
from app.models.product import Product
from app.models.user import User
from app.models.price_listing import PriceListing
from app.models.notification import Notification
from app.services.email_service import email_service
from app.schemas.alert import AlertCreate, AlertUpdate, AlertOut, WatchlistItemOut
from app.auth import get_current_user_optional, get_current_user

router = APIRouter(prefix="/api/alerts", tags=["Price Alerts & Watchlist"])

@router.post("", response_model=AlertOut)
async def create_price_alert(
    data: AlertCreate,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    prod = await db.get(Product, data.product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    email = user.email if user else (data.email.strip().lower() if data.email else None)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide an email address or log in to track price drops."
        )

    # Check if existing alert for this product & user/email exists
    existing = await db.execute(
        select(PriceAlert).where(
            PriceAlert.product_id == data.product_id,
            (PriceAlert.email == email) | (PriceAlert.user_id == (user.id if user else None))
        )
    )
    alert = existing.scalar_one_or_none()

    if alert:
        alert.target_price = data.target_price
        alert.currency = data.currency
        alert.is_active = True
        if user:
            alert.user_id = user.id
    else:
        alert = PriceAlert(
            user_id=user.id if user else None,
            product_id=data.product_id,
            email=email,
            target_price=data.target_price,
            currency=data.currency,
            is_active=True
        )
        db.add(alert)

    # Check if current price is already below target
    listings_res = await db.execute(
        select(PriceListing)
        .options(selectinload(PriceListing.store))
        .where(PriceListing.product_id == prod.id, PriceListing.is_available == True)
    )
    listings = listings_res.scalars().all()
    if listings:
        lowest_listing = min(listings, key=lambda x: x.price)
        alert.current_lowest_price = lowest_listing.price
        
        if lowest_listing.price <= data.target_price:
            alert.triggered_at = datetime.utcnow()
            alert.last_notified_price = lowest_listing.price
            # Create instant in-app notification
            notif = Notification(
                user_id=user.id if user else None,
                email=email,
                product_id=prod.id,
                alert_id=alert.id,
                title=f"🔥 Price Target Met: {prod.name}",
                message=(
                    f"Good news! {prod.name} is currently ฿{lowest_listing.price:,.2f} on {lowest_listing.store.name}, "
                    f"which is already below your target price of ฿{data.target_price:,.2f}!"
                ),
                old_price=data.target_price,
                new_price=lowest_listing.price,
                store_name=lowest_listing.store.name,
                product_url=lowest_listing.product_url,
                currency="THB",
                is_read=False
            )
            db.add(notif)
            
            # Dispatch Price Drop Email
            await email_service.send_price_drop_alert(
                to_email=email,
                product_name=prod.name,
                new_price=lowest_listing.price,
                target_price=data.target_price,
                store_name=lowest_listing.store.name,
                product_url=lowest_listing.product_url,
                product_image=prod.image_url,
                product_id=prod.id
            )
        else:
            # Dispatch Alert Confirmation Email
            await email_service.send_alert_confirmation(
                to_email=email,
                product_name=prod.name,
                target_price=data.target_price,
                current_lowest_price=lowest_listing.price,
                product_image=prod.image_url,
                product_id=prod.id
            )

    await db.commit()
    await db.refresh(alert)
    return alert

@router.get("/my-watchlist", response_model=List[WatchlistItemOut])
async def get_my_watchlist(
    user: Optional[User] = Depends(get_current_user_optional),
    email: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(PriceAlert)
        .options(
            selectinload(PriceAlert.product).selectinload(Product.listings).selectinload(PriceListing.store)
        )
        .order_by(desc(PriceAlert.created_at))
    )

    if user:
        query = query.where((PriceAlert.user_id == user.id) | (PriceAlert.email == user.email))
    elif email:
        query = query.where(PriceAlert.email == email.strip().lower())
    else:
        # Return all for demo / guest view
        query = query.limit(20)

    res = await db.execute(query)
    alerts = res.scalars().all()

    items = []
    for a in alerts:
        p = a.product
        if not p:
            continue
        
        active_listings = [l for l in p.listings if l.is_available and l.price > 0]
        if active_listings:
            best = min(active_listings, key=lambda x: x.price)
            lowest_p = best.price
            best_store = best.store.name if best.store else "Store"
            best_url = best.product_url
        else:
            lowest_p = p.msrp
            best_store = None
            best_url = None

        is_triggered = (lowest_p is not None and lowest_p <= a.target_price)

        items.append(WatchlistItemOut(
            id=a.id,
            product_id=p.id,
            product_name=p.name,
            product_brand=p.brand,
            product_category=p.category,
            product_image=p.image_url,
            target_price=a.target_price,
            current_lowest_price=lowest_p,
            best_store_name=best_store,
            best_product_url=best_url,
            currency=a.currency or "THB",
            is_triggered=is_triggered,
            is_active=a.is_active,
            created_at=a.created_at
        ))
    return items

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    alert = await db.get(PriceAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await db.delete(alert)
    await db.commit()
    return {"message": "Alert removed from watchlist", "id": alert_id}

@router.patch("/{alert_id}")
async def update_alert(
    alert_id: int,
    data: AlertUpdate,
    db: AsyncSession = Depends(get_db)
):
    alert = await db.get(PriceAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if data.target_price is not None:
        alert.target_price = data.target_price
    if data.is_active is not None:
        alert.is_active = data.is_active

    await db.commit()
    return {"message": "Alert updated", "id": alert_id}
