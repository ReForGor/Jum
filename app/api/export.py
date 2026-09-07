import csv
import io
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.product import Product
from app.models.price_listing import PriceListing
from app.models.store import Store

router = APIRouter(prefix="/api/export", tags=["Export"])

@router.get("/csv")
async def export_prices_csv(db: AsyncSession = Depends(get_db)):
    query = (
        select(Product)
        .options(selectinload(Product.listings).selectinload(PriceListing.store))
    )
    res = await db.execute(query)
    products = res.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Product ID", "Product Name", "Category", "Brand", "MSRP (THB)", 
        "Store Name", "Price (THB)", "Original Price (THB)", "Stock Status", 
        "Shipping Cost", "Total Price (THB)", "Rating", "Product URL", "Last Checked"
    ])

    for p in products:
        for l in p.listings:
            store_name = l.store.name if l.store else "Unknown"
            total = round(l.price + l.shipping_cost, 2)
            writer.writerow([
                p.id, p.name, p.category, p.brand, p.msrp,
                store_name, l.price, l.original_price or "", l.stock_status,
                l.shipping_cost, total, l.rating, l.product_url, l.last_checked.isoformat()
            ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=techprice_export.csv"}
    )
