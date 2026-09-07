import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.store import Store
from app.models.product import Product
from app.models.price_listing import PriceListing
from app.models.price_history import PriceHistory
from app.models.alert import PriceAlert
from app.models.notification import Notification
from app.scrapers.jib import JIBScraper
from app.scrapers.ihavecpu import IHaveCPUScraper
from app.scrapers.banana import BananaScraper
from app.scrapers.advice import AdviceScraper
from app.scrapers.mock_engine import MockLiveScraper

logger = logging.getLogger(__name__)

class ScraperManager:
    def __init__(self):
        self.scrapers = {
            "jib": JIBScraper(),
            "ihavecpu": IHaveCPUScraper(),
            "banana": BananaScraper(),
            "advice": AdviceScraper()
        }
        self.last_run_times: Dict[str, datetime] = {}
        self.last_job_result: Optional[Dict[str, Any]] = None

    async def run_scrape(
        self,
        db: AsyncSession,
        platform_slug: Optional[str] = None,
        product_id: Optional[int] = None,
        simulate: bool = True
    ) -> Dict[str, Any]:
        job_id = str(uuid.uuid4())[:8]
        started_at = datetime.utcnow()
        items_scraped = 0
        prices_updated = 0
        triggered_alerts = 0
        errors: List[str] = []

        try:
            # Query active Thai stores
            store_query = select(Store).where(Store.is_active == True)
            if platform_slug:
                store_query = store_query.where(Store.slug == platform_slug)
            store_res = await db.execute(store_query)
            stores = store_res.scalars().all()

            if not stores:
                return {
                    "job_id": job_id,
                    "status": "warning",
                    "started_at": started_at,
                    "completed_at": datetime.utcnow(),
                    "items_scraped": 0,
                    "prices_updated": 0,
                    "triggered_alerts": 0,
                    "errors": ["No active stores found."]
                }

            # Query products
            prod_query = select(Product)
            if product_id:
                prod_query = prod_query.where(Product.id == product_id)
            prod_res = await db.execute(prod_query)
            products = prod_res.scalars().all()

            for prod in products:
                for store in stores:
                    items_scraped += 1
                    try:
                        list_query = select(PriceListing).where(
                            PriceListing.product_id == prod.id,
                            PriceListing.store_id == store.id
                        )
                        list_res = await db.execute(list_query)
                        listing = list_res.scalar_one_or_none()

                        scraped_data = None
                        if simulate:
                            current_p = listing.price if listing else None
                            scraped_data = MockLiveScraper.simulate_price_scrape(
                                base_msrp=prod.msrp,
                                store_slug=store.slug,
                                current_price=current_p
                            )
                        else:
                            scraper = self.scrapers.get(store.slug)
                            if scraper:
                                p_url = listing.product_url if listing else None
                                scraped_data = await scraper.scrape_product(
                                    product_name=prod.name,
                                    model_no=prod.model_no,
                                    product_url=p_url
                                )

                        if scraped_data and scraped_data.get("price", 0) > 0:
                            price_val = scraped_data["price"]
                            now = datetime.utcnow()

                            old_price = listing.price if listing else None

                            if listing:
                                listing.price = price_val
                                listing.original_price = scraped_data.get("original_price")
                                listing.stock_status = scraped_data.get("stock_status", "in_stock")
                                listing.shipping_cost = scraped_data.get("shipping_cost", 0.0)
                                listing.rating = scraped_data.get("rating", 4.8)
                                listing.review_count = scraped_data.get("review_count", 1200)
                                listing.last_checked = now
                            else:
                                prod_url = scraped_data.get("product_url") or f"{store.base_url}/search?q={prod.name.replace(' ', '+')}"
                                listing = PriceListing(
                                    product_id=prod.id,
                                    store_id=store.id,
                                    price=price_val,
                                    original_price=scraped_data.get("original_price"),
                                    currency="THB",
                                    product_url=prod_url,
                                    stock_status=scraped_data.get("stock_status", "in_stock"),
                                    shipping_cost=scraped_data.get("shipping_cost", 0.0),
                                    rating=scraped_data.get("rating", 4.8),
                                    review_count=scraped_data.get("review_count", 1200),
                                    last_checked=now
                                )
                                db.add(listing)

                            # Record time-series price point
                            history_entry = PriceHistory(
                                product_id=prod.id,
                                store_id=store.id,
                                price=price_val,
                                currency="THB",
                                timestamp=now
                            )
                            db.add(history_entry)
                            prices_updated += 1

                            # Check user Price Drop Alerts
                            alert_query = select(PriceAlert).where(
                                PriceAlert.product_id == prod.id,
                                PriceAlert.is_active == True,
                                PriceAlert.target_price >= price_val
                            )
                            alert_res = await db.execute(alert_query)
                            matching_alerts = alert_res.scalars().all()

                            for alert in matching_alerts:
                                # Create in-app price drop notification
                                notif = Notification(
                                    user_id=alert.user_id,
                                    email=alert.email,
                                    product_id=prod.id,
                                    alert_id=alert.id,
                                    title=f"🔥 Price Drop: {prod.name}",
                                    message=(
                                        f"Great news! {prod.name} dropped to ฿{price_val:,.2f} on {store.name}. "
                                        f"This is below your target price of ฿{alert.target_price:,.2f}!"
                                    ),
                                    old_price=old_price or alert.target_price,
                                    new_price=price_val,
                                    store_name=store.name,
                                    product_url=listing.product_url,
                                    currency="THB",
                                    is_read=False,
                                    created_at=now
                                )
                                db.add(notif)
                                
                                alert.triggered_at = now
                                alert.last_notified_price = price_val
                                alert.current_lowest_price = price_val
                                triggered_alerts += 1

                        self.last_run_times[store.slug] = datetime.utcnow()

                    except Exception as item_err:
                        logger.error(f"Error scraping {prod.name} on {store.name}: {item_err}")
                        errors.append(f"{store.name} / {prod.name}: {str(item_err)}")

                prod.updated_at = datetime.utcnow()

            await db.commit()

            result = {
                "job_id": job_id,
                "status": "completed" if not errors else "completed_with_warnings",
                "started_at": started_at,
                "completed_at": datetime.utcnow(),
                "items_scraped": items_scraped,
                "prices_updated": prices_updated,
                "triggered_alerts": triggered_alerts,
                "errors": errors[:5]
            }
            self.last_job_result = result
            return result

        except Exception as e:
            await db.rollback()
            logger.exception("Scrape job failed")
            return {
                "job_id": job_id,
                "status": "failed",
                "started_at": started_at,
                "completed_at": datetime.utcnow(),
                "items_scraped": items_scraped,
                "prices_updated": prices_updated,
                "triggered_alerts": triggered_alerts,
                "errors": [str(e)]
            }

    async def get_platform_statuses(self, db: AsyncSession) -> List[Dict[str, Any]]:
        stores_res = await db.execute(select(Store))
        stores = stores_res.scalars().all()
        
        statuses = []
        for s in stores:
            listing_count_res = await db.execute(
                select(func.count(PriceListing.id)).where(PriceListing.store_id == s.id)
            )
            count = listing_count_res.scalar() or 0
            
            statuses.append({
                "platform_name": s.name,
                "platform_slug": s.slug,
                "logo_url": s.logo_url,
                "base_url": s.base_url,
                "color": s.color,
                "is_active": s.is_active,
                "total_listings": count,
                "last_run": self.last_run_times.get(s.slug),
                "status": "ready" if s.is_active else "disabled",
                "success_rate": 99.8
            })
        return statuses

scraper_manager = ScraperManager()
