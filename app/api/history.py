from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.product import Product
from app.models.store import Store
from app.models.price_history import PriceHistory
from app.models.price_listing import PriceListing
from app.schemas.history import ProductPriceHistoryOut, StoreHistorySeries

router = APIRouter(prefix="/api/prices", tags=["Price History"])

@router.get("/history/{product_id}", response_model=ProductPriceHistoryOut)
async def get_product_price_history(
    product_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of historical days to fetch"),
    db: AsyncSession = Depends(get_db)
):
    prod_res = await db.execute(
        select(Product)
        .options(selectinload(Product.listings).selectinload(PriceListing.store))
        .where(Product.id == product_id)
    )
    product = prod_res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    hist_query = (
        select(PriceHistory, Store)
        .join(Store, PriceHistory.store_id == Store.id)
        .where(
            PriceHistory.product_id == product_id,
            PriceHistory.timestamp >= cutoff_date
        )
        .order_by(asc(PriceHistory.timestamp))
    )
    hist_res = await db.execute(hist_query)
    records = hist_res.all()

    # Group by store
    store_series_map = {}
    all_prices = []

    for ph, st in records:
        all_prices.append(ph.price)
        if st.id not in store_series_map:
            store_series_map[st.id] = {
                "store_name": st.name,
                "store_id": st.id,
                "store_color": st.color or "#3b82f6",
                "data_points": []
            }
        store_series_map[st.id]["data_points"].append({
            "timestamp": ph.timestamp.isoformat(),
            "iso_date": ph.timestamp.strftime("%Y-%m-%d"),
            "date": ph.timestamp.strftime("%b %d"),
            "price": ph.price
        })

    # Current lowest
    active_listings = [l for l in product.listings if l.is_available and l.price > 0]
    current_lowest = min((l.price for l in active_listings), default=product.msrp or 0.0)
    lowest_hist = min(all_prices) if all_prices else current_lowest
    highest_hist = max(all_prices) if all_prices else (product.msrp or current_lowest)

    series_list = [
        StoreHistorySeries(**data) for data in store_series_map.values()
    ]

    return ProductPriceHistoryOut(
        product_id=product.id,
        product_name=product.name,
        lowest_historical_price=lowest_hist,
        highest_historical_price=highest_hist,
        current_lowest_price=current_lowest,
        series=series_list
    )
