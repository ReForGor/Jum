from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.product import Product
from app.models.price_listing import PriceListing

router = APIRouter(prefix="/api/search", tags=["Search"])

@router.get("/suggestions")
async def search_suggestions(
    q: str = Query(..., min_length=1, description="Search term for autocompletion"),
    limit: int = Query(8, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    search_term = f"%{q.lower()}%"
    query = (
        select(Product)
        .options(selectinload(Product.listings))
        .where(
            func.lower(Product.name).like(search_term) |
            func.lower(Product.brand).like(search_term) |
            func.lower(Product.category).like(search_term)
        )
        .limit(limit)
    )
    res = await db.execute(query)
    prods = res.scalars().all()

    suggestions = []
    for p in prods:
        active = [l for l in p.listings if l.is_available and l.price > 0]
        min_p = min((l.price for l in active), default=p.msrp)
        suggestions.append({
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "brand": p.brand,
            "image_url": p.image_url,
            "lowest_price": min_p,
            "store_count": len(active)
        })
    return suggestions
