from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.product import ProductSummaryOut

class AlertCreate(BaseModel):
    product_id: int
    target_price: float
    currency: str = "THB"
    email: Optional[str] = None

class AlertUpdate(BaseModel):
    target_price: Optional[float] = None
    is_active: Optional[bool] = None

class AlertOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    product_id: int
    email: str
    target_price: float
    currency: str
    current_lowest_price: Optional[float] = None
    last_notified_price: Optional[float] = None
    is_active: bool
    triggered_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WatchlistItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_brand: str
    product_category: str
    product_image: Optional[str] = None
    target_price: float
    current_lowest_price: Optional[float] = None
    best_store_name: Optional[str] = None
    best_product_url: Optional[str] = None
    currency: str = "THB"
    is_triggered: bool = False
    is_active: bool = True
    created_at: datetime
