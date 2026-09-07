from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_id = Column(Integer, ForeignKey("price_alerts.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    old_price = Column(Float, nullable=True)
    new_price = Column(Float, nullable=False)
    store_name = Column(String(100), nullable=True)
    product_url = Column(String(1000), nullable=True)
    currency = Column(String(10), default="THB")
    
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="notifications")
    product = relationship("Product")

    def __repr__(self):
        return f"<Notification {self.title} price={self.new_price} is_read={self.is_read}>"
