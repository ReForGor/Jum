import random
from typing import Dict, Any, Optional

class MockLiveScraper:
    """
    Simulates real-time pricing dynamics across Thai IT Equipment platforms:
    JIB, iHaveCPU, BaNANA, and Advice.
    """
    @staticmethod
    def simulate_price_scrape(base_msrp: float, store_slug: str, current_price: Optional[float] = None) -> Dict[str, Any]:
        # Always prioritize existing verified real price to prevent random spikes
        base = current_price if (current_price and current_price > 0) else (base_msrp or 18900.0)
        
        # Real prices in stores stay virtually identical to the live scraped value
        simulated_price = float(base)
        original_price = round(base * 1.08, 2)

        # Stock status
        stock_roll = random.random()
        if stock_roll < 0.88:
            stock = "in_stock"
        elif stock_roll < 0.96:
            stock = "low_stock"
        else:
            stock = "backorder"

        shipping = 0.0 # Free shipping standard in Thailand above ฿1,000
        
        return {
            "price": float(simulated_price),
            "original_price": float(original_price) if original_price else None,
            "stock_status": stock,
            "shipping_cost": shipping,
            "rating": round(random.uniform(4.7, 4.9), 1),
            "review_count": random.randint(350, 4800)
        }
