from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.store import StoreOut

class PriceListingBase(BaseModel):
    product_id: int
    store_id: int
    price: float
    original_price: Optional[float] = None
    currency: str = "USD"
    product_url: str
    stock_status: str = "in_stock"
    shipping_cost: float = 0.0
    seller_name: Optional[str] = None
    rating: float = 4.8
    review_count: int = 0
    is_available: bool = True

class PriceListingCreate(PriceListingBase):
    pass

class PriceListingOut(PriceListingBase):
    id: int
    last_checked: datetime
    store: Optional[StoreOut] = None

    model_config = ConfigDict(from_attributes=True)

class PlatformComparisonItem(BaseModel):
    store_id: int
    store_name: str
    store_slug: str
    store_logo: Optional[str] = None
    store_color: str = "#3b82f6"
    price: float
    original_price: Optional[float] = None
    currency: str = "USD"
    discount_percent: float = 0.0
    price_diff_from_lowest: float = 0.0
    is_lowest: bool = False
    stock_status: str = "in_stock"
    shipping_cost: float = 0.0
    total_price: float
    product_url: str
    rating: float = 4.8
    review_count: int = 0
    last_checked: datetime
