from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.product import Product
from app.models.price_listing import PriceListing
from app.models.store import Store
from app.schemas.product import ProductSummaryOut, ProductDetailOut, ProductCreate
from app.schemas.listing import PlatformComparisonItem

router = APIRouter(prefix="/api", tags=["Products"])

@router.get("/products", response_model=List[ProductSummaryOut])
async def list_products(
    q: Optional[str] = Query(None, description="Search keyword in product name or description"),
    category: Optional[str] = Query(None, description="Filter by IT equipment category"),
    brand: Optional[str] = Query(None, description="Filter by brand name"),
    store_slug: Optional[str] = Query(None, description="Filter by store availability"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    sort_by: str = Query("cheapest", description="Sort by: cheapest, expensive, discount, name, newest"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(Product).options(
        selectinload(Product.listings).selectinload(PriceListing.store)
    )

    if q:
        search_pattern = f"%{q.lower()}%"
        query = query.where(
            func.lower(Product.name).like(search_pattern) | 
            func.lower(Product.brand).like(search_pattern) |
            func.lower(Product.description).like(search_pattern)
        )

    if category and category != "All":
        query = query.where(Product.category == category)

    if brand and brand != "All":
        query = query.where(Product.brand == brand)

    res = await db.execute(query)
    all_products = res.scalars().all()

    # Process pricing summaries and filters
    results = []
    for prod in all_products:
        active_listings = [l for l in prod.listings if l.is_available and l.price > 0]
        
        if store_slug:
            active_listings = [l for l in active_listings if l.store and l.store.slug == store_slug]
            if not active_listings:
                continue

        if not active_listings:
            lowest_p = prod.msrp
            highest_p = prod.msrp
            best_listing = None
            max_discount = 0.0
        else:
            sorted_listings = sorted(active_listings, key=lambda x: x.price)
            lowest_p = sorted_listings[0].price
            highest_p = max(l.price for l in active_listings)
            best_listing = sorted_listings[0]
            
            discounts = [
                ((l.original_price - l.price) / l.original_price * 100)
                for l in active_listings if l.original_price and l.original_price > l.price
            ]
            max_discount = max(discounts) if discounts else 0.0

        # Price range filter check
        if min_price is not None and lowest_p is not None and lowest_p < min_price:
            continue
        if max_price is not None and lowest_p is not None and lowest_p > max_price:
            continue

        item = ProductSummaryOut(
            id=prod.id,
            name=prod.name,
            slug=prod.slug,
            category=prod.category,
            brand=prod.brand,
            model_no=prod.model_no,
            image_url=prod.image_url,
            description=prod.description,
            msrp=prod.msrp,
            specs=prod.specs or {},
            created_at=prod.created_at,
            updated_at=prod.updated_at,
            lowest_price=lowest_p,
            highest_price=highest_p,
            store_count=len(active_listings),
            best_store_name=best_listing.store.name if best_listing and best_listing.store else None,
            best_store_logo=best_listing.store.logo_url if best_listing and best_listing.store else None,
            best_product_url=best_listing.product_url if best_listing else None,
            max_discount_percent=round(max_discount, 1)
        )
        results.append(item)

    # Sorting
    if sort_by == "cheapest":
        results.sort(key=lambda x: (x.lowest_price or 999999))
    elif sort_by == "expensive":
        results.sort(key=lambda x: (x.lowest_price or 0), reverse=True)
    elif sort_by == "discount":
        results.sort(key=lambda x: x.max_discount_percent, reverse=True)
    elif sort_by == "name":
        results.sort(key=lambda x: x.name)
    elif sort_by == "newest":
        results.sort(key=lambda x: x.created_at, reverse=True)

    return results[offset : offset + limit]

@router.get("/products/{product_id}", response_model=ProductDetailOut)
async def get_product_detail(product_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(Product)
        .options(selectinload(Product.listings).selectinload(PriceListing.store))
        .where(Product.id == product_id)
    )
    res = await db.execute(query)
    prod = res.scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    active_listings = [l for l in prod.listings if l.is_available and l.price > 0]
    
    if not active_listings:
        return ProductDetailOut(
            id=prod.id,
            name=prod.name,
            slug=prod.slug,
            category=prod.category,
            brand=prod.brand,
            model_no=prod.model_no,
            image_url=prod.image_url,
            description=prod.description,
            msrp=prod.msrp,
            specs=prod.specs or {},
            created_at=prod.created_at,
            updated_at=prod.updated_at,
            lowest_price=prod.msrp,
            highest_price=prod.msrp,
            avg_price=prod.msrp,
            total_savings=0.0,
            best_store=None,
            platforms=[]
        )

    # Find lowest price
    sorted_listings = sorted(active_listings, key=lambda x: (x.price + x.shipping_cost))
    lowest_total = sorted_listings[0].price + sorted_listings[0].shipping_cost
    lowest_raw_price = sorted_listings[0].price
    highest_price = max(l.price for l in active_listings)
    avg_price = round(sum(l.price for l in active_listings) / len(active_listings), 2)
    max_savings = round(highest_price - lowest_raw_price, 2)

    platform_items = []
    for l in sorted_listings:
        store = l.store
        total_p = round(l.price + l.shipping_cost, 2)
        diff_from_lowest = round(total_p - lowest_total, 2)
        disc_pct = (
            round(((l.original_price - l.price) / l.original_price) * 100, 1)
            if l.original_price and l.original_price > l.price
            else 0.0
        )

        platform_items.append(
            PlatformComparisonItem(
                store_id=l.store_id,
                store_name=store.name if store else "Unknown",
                store_slug=store.slug if store else "unknown",
                store_logo=store.logo_url if store else None,
                store_color=store.color if store else "#3b82f6",
                price=l.price,
                original_price=l.original_price,
                currency=l.currency,
                discount_percent=disc_pct,
                price_diff_from_lowest=diff_from_lowest,
                is_lowest=(l.id == sorted_listings[0].id),
                stock_status=l.stock_status,
                shipping_cost=l.shipping_cost,
                total_price=total_p,
                product_url=l.product_url,
                rating=l.rating,
                review_count=l.review_count,
                last_checked=l.last_checked
            )
        )

    return ProductDetailOut(
        id=prod.id,
        name=prod.name,
        slug=prod.slug,
        category=prod.category,
        brand=prod.brand,
        model_no=prod.model_no,
        image_url=prod.image_url,
        description=prod.description,
        msrp=prod.msrp,
        specs=prod.specs or {},
        created_at=prod.created_at,
        updated_at=prod.updated_at,
        lowest_price=lowest_raw_price,
        highest_price=highest_price,
        avg_price=avg_price,
        total_savings=max_savings,
        best_store=sorted_listings[0].store.name if sorted_listings[0].store else None,
        platforms=platform_items
    )

@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(Product.category, func.count(Product.id)).group_by(Product.category)
    )
    data = res.all()
    return [{"category": row[0], "count": row[1]} for row in data]

@router.get("/brands")
async def get_brands(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(Product.brand, func.count(Product.id)).group_by(Product.brand)
    )
    data = res.all()
    return [{"brand": row[0], "count": row[1]} for row in data]
