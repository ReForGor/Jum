from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    logo_url = Column(String(500), nullable=True)
    base_url = Column(String(500), nullable=False)
    color = Column(String(20), default="#3b82f6")  # Accent color for UI badges
    scraper_type = Column(String(50), default="generic")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    listings = relationship("PriceListing", back_populates="store", cascade="all, delete-orphan")
    price_histories = relationship("PriceHistory", back_populates="store", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Store {self.name}>"
