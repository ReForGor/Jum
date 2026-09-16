import re
import random
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import httpx
from bs4 import BeautifulSoup
from app.config import settings

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
]

class BasePlatformScraper(ABC):
    platform_name: str = "Generic Platform"
    platform_slug: str = "generic"
    base_url: str = ""

    def __init__(self):
        self.headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    async def fetch_html(self, url: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=settings.REQUEST_TIMEOUT) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.text
                logger.warning(f"[{self.platform_name}] Failed to fetch {url}, status: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"[{self.platform_name}] Exception fetching {url}: {e}")
            return None

    def clean_price(self, price_val: Any) -> Optional[float]:
        if price_val is None:
            return None
        if isinstance(price_val, (int, float)):
            val = float(price_val)
            return round(val, 2) if val > 0 else None
        cleaned = re.sub(r"[^\d.]", "", str(price_val))
        try:
            val = float(cleaned)
            return round(val, 2) if val > 0 else None
        except (ValueError, TypeError):
            return None

    @abstractmethod
    async def scrape_product(self, product_name: str, model_no: Optional[str], product_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Return dict matching:
        {
            "price": float,
            "original_price": float or None,
            "stock_status": "in_stock" | "out_of_stock" | "backorder",
            "shipping_cost": float,
            "rating": float,
            "review_count": int,
            "product_url": str
        }
        """
        pass
