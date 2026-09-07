import random
from typing import Dict, Any, Optional

class MockLiveScraper:
    """
    Simulates real-time pricing dynamics across Thai IT Equipment platforms:
    JIB, iHaveCPU, BaNANA, and Advice.
    """
    @staticmethod
    def simulate_price_scrape(base_msrp: float, store_slug: str, current_price: Optional[float] = None) -> Dict[str, Any]:
        msrp = base_msrp or 18900.0
        
        # Thai store pricing characteristics
        multipliers = {
            "jib": (0.93, 1.02),       # JIB official retail baseline, high stock reliability
            "ihavecpu": (0.88, 0.98),  # iHaveCPU competitive enthusiast pricing & GPU promos
            "banana": (0.94, 1.03),    # BaNANA IT nationwide retail warranty & points
            "advice": (0.89, 1.00)     # Advice IT wholesale & flash sales
        }
        
        low_mult, high_mult = multipliers.get(store_slug, (0.92, 1.02))
        
        # 12% chance of special flash sale discount (12-18% off)
        is_flash_sale = random.random() < 0.12
        if is_flash_sale:
            simulated_price = round(msrp * random.uniform(0.82, 0.88) / 10) * 10
            original_price = round(msrp * 1.05 / 10) * 10
        else:
            simulated_price = round(msrp * random.uniform(low_mult, high_mult) / 10) * 10
            original_price = round(msrp * 1.06 / 10) * 10 if simulated_price < msrp else None

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
