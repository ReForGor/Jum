from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    model_no = Column(String(100), nullable=True)
    image_url = Column(String(1000), nullable=True)
    description = Column(Text, nullable=True)
    msrp = Column(Float, nullable=True)  # Manufacturer Suggested Retail Price
    specs = Column(JSON, default=dict)   # E.g. {"vram": "32GB GDDR7", "tdp": "600W", "interface": "PCIe 5.0"}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    listings = relationship("PriceListing", back_populates="product", cascade="all, delete-orphan")
    price_histories = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    alerts = relationship("PriceAlert", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.name}>"
