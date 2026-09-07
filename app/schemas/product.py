from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.listing import PriceListingOut, PlatformComparisonItem

class ProductBase(BaseModel):
    name: str
    slug: str
    category: str
    brand: str
    model_no: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    msrp: Optional[float] = None
    specs: Dict[str, Any] = {}

class ProductCreate(ProductBase):
    pass

class ProductSummaryOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    store_count: int = 0
    best_store_name: Optional[str] = None
    best_store_logo: Optional[str] = None
    best_product_url: Optional[str] = None
    max_discount_percent: float = 0.0

    model_config = ConfigDict(from_attributes=True)

class ProductDetailOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    avg_price: Optional[float] = None
    total_savings: Optional[float] = None
    best_store: Optional[str] = None
    platforms: List[PlatformComparisonItem] = []

    model_config = ConfigDict(from_attributes=True)
