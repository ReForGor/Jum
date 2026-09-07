import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, delete
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.database import get_db
from app.models.product import Product
from app.models.store import Store
from app.models.price_listing import PriceListing
from app.models.price_history import PriceHistory
from app.models.alert import PriceAlert
from app.models.user import User
from app.models.notification import Notification
from app.auth import get_current_admin
from app.schemas.product import ProductSummaryOut, ProductDetailOut

router = APIRouter(prefix="/api/admin", tags=["Admin Management"], dependencies=[Depends(get_current_admin)])

# Schemas for Admin operations
class ProductCreateAdmin(BaseModel):
    name: str
    category: str
    brand: str
    model_no: Optional[str] = None
    msrp: float
    image_url: Optional[str] = None
    description: Optional[str] = None
    specs: Dict[str, Any] = {}

class ProductUpdateAdmin(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    model_no: Optional[str] = None
    msrp: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    specs: Optional[Dict[str, Any]] = None

class ListingCreateAdmin(BaseModel):
    product_id: int
    store_id: int
    price: float
    original_price: Optional[float] = None
    currency: str = "THB"
    product_url: str
    stock_status: str = "in_stock"
    shipping_cost: float = 0.0

class ListingUpdateAdmin(BaseModel):
    price: Optional[float] = None
    original_price: Optional[float] = None
    stock_status: Optional[str] = None
    product_url: Optional[str] = None
    shipping_cost: Optional[float] = None

class StoreUpdateAdmin(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None

class BroadcastNotificationRequest(BaseModel):
    product_id: Optional[int] = None
    title: str
    message: str
    new_price: Optional[float] = None
    store_name: Optional[str] = "JIB / Advice"

# ----------------- Dashboard Analytics -----------------

@router.get("/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    prod_count = (await db.execute(select(func.count(Product.id)))).scalar() or 0
    store_count = (await db.execute(select(func.count(Store.id)))).scalar() or 0
    listing_count = (await db.execute(select(func.count(PriceListing.id)))).scalar() or 0
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    alert_count = (await db.execute(select(func.count(PriceAlert.id)))).scalar() or 0
    notif_count = (await db.execute(select(func.count(Notification.id)))).scalar() or 0

    # Recent 5 notifications
    notifs_res = await db.execute(
        select(Notification).order_by(desc(Notification.created_at)).limit(5)
    )
    recent_notifs = notifs_res.scalars().all()

    # Stores breakdown
    stores_res = await db.execute(select(Store))
    stores = stores_res.scalars().all()
    stores_data = []
    for s in stores:
        cnt = (await db.execute(
            select(func.count(PriceListing.id)).where(PriceListing.store_id == s.id)
        )).scalar() or 0
        stores_data.append({
            "id": s.id,
            "name": s.name,
            "slug": s.slug,
            "color": s.color,
            "is_active": s.is_active,
            "listings_count": cnt
        })

    return {
        "products_count": prod_count,
        "stores_count": store_count,
        "listings_count": listing_count,
        "users_count": user_count,
        "alerts_count": alert_count,
        "notifications_count": notif_count,
        "stores": stores_data,
        "recent_notifications": [
            {
                "id": n.id,
                "title": n.title,
                "store_name": n.store_name,
                "new_price": n.new_price,
                "created_at": n.created_at
            }
            for n in recent_notifs
        ]
    }

# ----------------- Products Management -----------------

@router.get("/products")
async def list_admin_products(
    q: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Product).options(
        selectinload(Product.listings).selectinload(PriceListing.store)
    ).order_by(desc(Product.created_at))

    if q:
        search_pat = f"%{q.lower()}%"
        query = query.where(
            func.lower(Product.name).like(search_pat) |
            func.lower(Product.brand).like(search_pat)
        )
    if category and category != "All":
        query = query.where(Product.category == category)

    res = await db.execute(query)
    prods = res.scalars().all()

    results = []
    for p in prods:
        active = [l for l in p.listings if l.is_available and l.price > 0]
        min_p = min((l.price for l in active), default=p.msrp)
        max_p = max((l.price for l in active), default=p.msrp)
        best = min(active, key=lambda x: x.price) if active else None

        results.append({
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "category": p.category,
            "brand": p.brand,
            "model_no": p.model_no,
            "msrp": p.msrp,
            "image_url": p.image_url,
            "description": p.description,
            "specs": p.specs or {},
            "lowest_price": min_p,
            "highest_price": max_p,
            "store_count": len(active),
            "best_store": best.store.name if best and best.store else None,
            "listings": [
                {
                    "id": l.id,
                    "store_id": l.store_id,
                    "store_name": l.store.name if l.store else "Unknown",
                    "store_color": l.store.color if l.store else "#3b82f6",
                    "price": l.price,
                    "original_price": l.original_price,
                    "stock_status": l.stock_status,
                    "product_url": l.product_url,
                    "last_checked": l.last_checked
                }
                for l in p.listings
            ]
        })
    return results

@router.post("/products")
async def create_product(
    data: ProductCreateAdmin,
    db: AsyncSession = Depends(get_db)
):
    slug_base = re.sub(r'[^a-zA-Z0-9]+', '-', data.name.lower()).strip('-')
    # ensure unique slug
    existing_slug = await db.execute(select(Product).where(Product.slug == slug_base))
    if existing_slug.scalar_one_or_none():
        slug_base = f"{slug_base}-{int(datetime.utcnow().timestamp())}"

    prod = Product(
        name=data.name.strip(),
        slug=slug_base,
        category=data.category,
        brand=data.brand.strip(),
        model_no=data.model_no,
        msrp=data.msrp,
        image_url=data.image_url or "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=400",
        description=data.description,
        specs=data.specs or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(prod)
    await db.commit()
    await db.refresh(prod)

    # Auto create initial listings on all active stores (JIB, iHaveCPU, BaNANA, Advice)
    stores_res = await db.execute(select(Store).where(Store.is_active == True))
    stores = stores_res.scalars().all()
    now = datetime.utcnow()
    for s in stores:
        listing = PriceListing(
            product_id=prod.id,
            store_id=s.id,
            price=data.msrp,
            original_price=data.msrp,
            currency="THB",
            product_url=f"{s.base_url}/search?q={prod.name.replace(' ', '+')}",
            stock_status="in_stock",
            shipping_cost=0.0,
            last_checked=now
        )
        db.add(listing)

    await db.commit()
    return {"message": "Product created successfully", "id": prod.id, "slug": prod.slug}

@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    data: ProductUpdateAdmin,
    db: AsyncSession = Depends(get_db)
):
    prod = await db.get(Product, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    if data.name is not None: prod.name = data.name.strip()
    if data.category is not None: prod.category = data.category
    if data.brand is not None: prod.brand = data.brand.strip()
    if data.model_no is not None: prod.model_no = data.model_no
    if data.msrp is not None: prod.msrp = data.msrp
    if data.image_url is not None: prod.image_url = data.image_url
    if data.description is not None: prod.description = data.description
    if data.specs is not None: prod.specs = data.specs
    prod.updated_at = datetime.utcnow()

    await db.commit()
    return {"message": "Product updated successfully", "id": product_id}

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    prod = await db.get(Product, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(prod)
    await db.commit()
    return {"message": "Product deleted successfully", "id": product_id}

# ----------------- Store Listings Management -----------------

@router.post("/listings")
async def create_or_override_listing(
    data: ListingCreateAdmin,
    db: AsyncSession = Depends(get_db)
):
    existing = await db.execute(
        select(PriceListing).where(
            PriceListing.product_id == data.product_id,
            PriceListing.store_id == data.store_id
        )
    )
    listing = existing.scalar_one_or_none()
    now = datetime.utcnow()

    if listing:
        listing.price = data.price
        listing.original_price = data.original_price
        listing.stock_status = data.stock_status
        listing.product_url = data.product_url
        listing.shipping_cost = data.shipping_cost
        listing.last_checked = now
    else:
        listing = PriceListing(
            product_id=data.product_id,
            store_id=data.store_id,
            price=data.price,
            original_price=data.original_price,
            currency=data.currency,
            product_url=data.product_url,
            stock_status=data.stock_status,
            shipping_cost=data.shipping_cost,
            last_checked=now
        )
        db.add(listing)

    # Add historical price point
    db.add(PriceHistory(
        product_id=data.product_id,
        store_id=data.store_id,
        price=data.price,
        currency="THB",
        timestamp=now
    ))

    await db.commit()
    return {"message": "Store price listing saved", "product_id": data.product_id, "store_id": data.store_id}

@router.put("/listings/{listing_id}")
async def update_listing(
    listing_id: int,
    data: ListingUpdateAdmin,
    db: AsyncSession = Depends(get_db)
):
    listing = await db.get(PriceListing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if data.price is not None:
        listing.price = data.price
        db.add(PriceHistory(
            product_id=listing.product_id,
            store_id=listing.store_id,
            price=data.price,
            currency="THB",
            timestamp=datetime.utcnow()
        ))
    if data.original_price is not None: listing.original_price = data.original_price
    if data.stock_status is not None: listing.stock_status = data.stock_status
    if data.product_url is not None: listing.product_url = data.product_url
    if data.shipping_cost is not None: listing.shipping_cost = data.shipping_cost
    listing.last_checked = datetime.utcnow()

    await db.commit()
    return {"message": "Listing updated", "id": listing_id}

@router.delete("/listings/{listing_id}")
async def delete_listing(
    listing_id: int,
    db: AsyncSession = Depends(get_db)
):
    listing = await db.get(PriceListing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    await db.delete(listing)
    await db.commit()
    return {"message": "Listing deleted", "id": listing_id}

# ----------------- Users Management -----------------

@router.get("/users")
async def list_admin_users(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).order_by(desc(User.created_at)))
    users = res.scalars().all()

    results = []
    for u in users:
        alerts_cnt = (await db.execute(
            select(func.count(PriceAlert.id)).where(PriceAlert.user_id == u.id)
        )).scalar() or 0

        results.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "is_admin": u.is_admin,
            "alerts_count": alerts_cnt,
            "created_at": u.created_at
        })
    return results

@router.patch("/users/{user_id}/toggle-admin")
async def toggle_user_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_admin = not user.is_admin
    await db.commit()
    return {"message": f"User {user.username} admin status set to {user.is_admin}", "is_admin": user.is_admin}

# ----------------- Alerts & Notification Broadcast -----------------

@router.get("/alerts")
async def list_all_alerts(db: AsyncSession = Depends(get_db)):
    query = (
        select(PriceAlert)
        .options(selectinload(PriceAlert.product), selectinload(PriceAlert.user))
        .order_by(desc(PriceAlert.created_at))
    )
    res = await db.execute(query)
    alerts = res.scalars().all()

    return [
        {
            "id": a.id,
            "user_id": a.user_id,
            "username": a.user.username if a.user else "Guest",
            "email": a.email,
            "product_id": a.product_id,
            "product_name": a.product.name if a.product else "Unknown",
            "target_price": a.target_price,
            "current_lowest_price": a.current_lowest_price,
            "is_active": a.is_active,
            "triggered_at": a.triggered_at,
            "created_at": a.created_at
        }
        for a in alerts
    ]

@router.post("/broadcast-notification")
async def broadcast_notification(
    data: BroadcastNotificationRequest,
    db: AsyncSession = Depends(get_db)
):
    # Find target users
    users_res = await db.execute(select(User))
    users = users_res.scalars().all()

    now = datetime.utcnow()
    prod = await db.get(Product, data.product_id) if data.product_id else None
    prod_id = prod.id if prod else 1
    price_val = data.new_price or (prod.msrp if prod else 10000.0)

    count = 0
    for u in users:
        notif = Notification(
            user_id=u.id,
            email=u.email,
            product_id=prod_id,
            title=data.title,
            message=data.message,
            new_price=price_val,
            store_name=data.store_name,
            product_url=f"https://www.jib.co.th",
            currency="THB",
            is_read=False,
            created_at=now
        )
        db.add(notif)
        count += 1

    await db.commit()
    return {"message": f"Broadcast notification sent to {count} users", "dispatched_count": count}
