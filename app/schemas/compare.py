from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.product import ProductDetailOut

class SpecRow(BaseModel):
    spec_key: str
    spec_label: str
    values: Dict[int, Any]

class MultiProductCompareResponse(BaseModel):
    products: List[ProductDetailOut]
    spec_matrix: List[SpecRow]
    price_winner_id: Optional[int] = None
    value_score_leader_id: Optional[int] = None

class AlertCreate(BaseModel):
    product_id: int
    email: str
    target_price: float
    currency: str = "USD"

class AlertOut(BaseModel):
    id: int
    product_id: int
    email: str
    target_price: float
    currency: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
