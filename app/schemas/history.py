from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class PriceHistoryPoint(BaseModel):
    timestamp: datetime
    price: float
    store_name: str
    store_id: int
    store_color: str

class StoreHistorySeries(BaseModel):
    store_name: str
    store_id: int
    store_color: str
    data_points: List[Dict[str, Any]] # [{"date": "2025-01-01", "price": 499.99}]

class ProductPriceHistoryOut(BaseModel):
    product_id: int
    product_name: str
    lowest_historical_price: float
    highest_historical_price: float
    current_lowest_price: float
    series: List[StoreHistorySeries]
