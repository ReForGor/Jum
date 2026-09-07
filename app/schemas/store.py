from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class StoreBase(BaseModel):
    name: str
    slug: str
    logo_url: Optional[str] = None
    base_url: str
    color: Optional[str] = "#3b82f6"
    scraper_type: Optional[str] = "generic"
    is_active: bool = True

class StoreCreate(StoreBase):
    pass

class StoreOut(StoreBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
