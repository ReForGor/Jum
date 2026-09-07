from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    target_price = Column(Float, nullable=False)
    currency = Column(String(10), default="THB")
    current_lowest_price = Column(Float, nullable=True)
    last_notified_price = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="alerts")
    product = relationship("Product", back_populates="alerts")

    def __repr__(self):
        return f"<PriceAlert user={self.user_id} {self.email} target={self.target_price}>"
