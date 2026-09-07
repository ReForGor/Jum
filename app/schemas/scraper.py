from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ScraperRunRequest(BaseModel):
    platform_slug: Optional[str] = None # None means all platforms
    product_id: Optional[int] = None    # None means all products
    simulate_live: bool = True

class ScraperPlatformStatus(BaseModel):
    platform_name: str
    platform_slug: str
    is_active: bool
    total_listings: int
    last_run: Optional[datetime] = None
    status: str = "idle" # "idle", "running", "error", "ready"
    success_rate: float = 100.0

class ScrapeJobResult(BaseModel):
    job_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    items_scraped: int
    prices_updated: int
    errors: List[str] = []
