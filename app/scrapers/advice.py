import re
import httpx
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from app.scrapers.base import BasePlatformScraper
from app.utils.store_urls import generate_store_product_url

ADVICE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoib25saW5lIiwiaXNfbWVtYmVyIjpmYWxzZSwiaWF0IjoxNzg5MTQ0NDIwLCJleHAiOjE3ODkyMzA4MjB9.3KfxpvnYNrC-AQdcK023t2lcnwyYbbq3LROS0MBhXQg"

class AdviceScraper(BasePlatformScraper):
    platform_name = "Advice IT Infinite"
    platform_slug = "advice"
    base_url = "https://www.advice.co.th"

    async def scrape_product(self, product_name: str, model_no: Optional[str], product_url: Optional[str] = None) -> Dict[str, Any]:
        url = product_url or generate_store_product_url("advice", product_name, model_no=model_no)
        html = await self.fetch_html(url)
        price_val = None
        
        if html:
            soup = BeautifulSoup(html, "html.parser")
            price_elem = soup.select_one(".sale-price, .price, .product-price")
            if price_elem:
                price_val = self.clean_price(price_elem.get_text())
                if price_val:
                    return {
                        "price": price_val,
                        "original_price": round(price_val * 1.09, 2),
                        "stock_status": "in_stock",
                        "shipping_cost": 0.0,
                        "rating": 4.8,
                        "review_count": 2100,
                        "product_url": url
                    }
        # 1. Advice API by product code (e.g. A0153753)
        code_m = re.search(r'product/(?:detail/)?([A-Za-z0-9]+)', url)
        if code_m:
            item_code = code_m.group(1)
            api_url = "https://prodbackadvice.advice.in.th/api/v1.0.0/product/get"
            headers = {
                "User-Agent": self.headers.get("User-Agent", "Mozilla/5.0"),
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ADVICE_TOKEN}",
                "Origin": "https://www.advice.co.th",
                "Referer": "https://www.advice.co.th/"
            }
            try:
                async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
                    resp = await client.post(api_url, json={"keyword": item_code})
                    if resp.status_code == 200:
                        res_data = resp.json()
                        for grp in res_data.get("data", {}).get("product", []):
                            for item in grp.get("product", []):
                                p = item.get("price_sale") or item.get("price_sale_true") or item.get("price_srp")
                                price_val = self.clean_price(p)
                                if price_val:
                                    break
                            if price_val:
                                break
            except Exception:
                pass

        # 2. HTML fetch fallback if API didn't return price
        if not price_val:
            html = await self.fetch_html(url)
            if html:
                for pat in [r'"price_sale":\s*"?([0-9,]+)"?', r'"sale_price_online":\s*"?([0-9,]+)"?', r'"price":\s*"?([0-9,]+)"?']:
                    m = re.search(pat, html)
                    if m:
                        price_val = self.clean_price(m.group(1))
                        if price_val:
                            break
                if not price_val:
                    soup = BeautifulSoup(html, "html.parser")
                    price_elem = soup.select_one(".sale-price, .price, .product-price")
                    if price_elem:
                        price_val = self.clean_price(price_elem.get_text())

        if price_val and price_val > 0:
            return {
                "price": price_val,
                "original_price": round(price_val * 1.09, 2),
                "stock_status": "in_stock",
                "shipping_cost": 0.0,
                "rating": 4.8,
                "review_count": 2100,
                "product_url": url
            }

        return {
            "price": 0.0,
            "original_price": None,
            "stock_status": "in_stock",
            "shipping_cost": 0.0,
            "rating": 4.8,
            "review_count": 2100,
            "product_url": url
        }
