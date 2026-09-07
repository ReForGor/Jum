from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class PriceListing(Base):
    __tablename__ = "price_listings"
    __table_args__ = (
        UniqueConstraint('product_id', 'store_id', name='_product_store_uc'),
    )

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    
    price = Column(Float, nullable=False, index=True)
    original_price = Column(Float, nullable=True)  # List price before discount
    currency = Column(String(10), default="USD")
    product_url = Column(String(1000), nullable=False)
    
    stock_status = Column(String(50), default="in_stock")  # in_stock, out_of_stock, backorder, pre_order
    shipping_cost = Column(Float, default=0.0)
    seller_name = Column(String(100), nullable=True)
    rating = Column(Float, default=4.8)
    review_count = Column(Integer, default=0)
    
    last_checked = Column(DateTime, default=datetime.utcnow, index=True)
    is_available = Column(Boolean, default=True)

    product = relationship("Product", back_populates="listings")
    store = relationship("Store", back_populates="listings")

    def __repr__(self):
        return f"<PriceListing product_id={self.product_id} store_id={self.store_id} price={self.price}>"
