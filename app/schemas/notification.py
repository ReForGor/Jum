from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class NotificationOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    email: Optional[str] = None
    product_id: int
    alert_id: Optional[int] = None
    title: str
    message: str
    old_price: Optional[float] = None
    new_price: float
    store_name: Optional[str] = None
    product_url: Optional[str] = None
    currency: str = "THB"
    is_read: bool = False
    created_at: datetime
    product_name: Optional[str] = None
    product_image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
