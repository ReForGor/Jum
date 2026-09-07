from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    product = relationship("Product", back_populates="price_histories")
    store = relationship("Store", back_populates="price_histories")

    def __repr__(self):
        return f"<PriceHistory prod={self.product_id} store={self.store_id} price={self.price} at={self.timestamp}>"
