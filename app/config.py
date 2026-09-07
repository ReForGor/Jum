import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    PROJECT_NAME: str = "TechPrice - Thai IT Equipment Price Aggregator"
    PROJECT_DESCRIPTION: str = "Compare IT hardware & equipment prices across JIB, iHaveCPU, BaNANA IT, Advice, and more."
    PROJECT_VERSION: str = "2.0.0"
    BASE_DIR: Path = BASE_DIR
    
    # PostgreSQL connection string (Neon Serverless Postgres)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://neondb_owner:npg_ExaMXrTcA5C3@ep-cool-firefly-b33d39wh.c-4.ap-southeast-1.aws.neon.tech/neondb"
    )
    
    # JWT Authentication settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "techprice-super-secure-secret-key-2026")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 72
    
    # Scraper settings
    DEFAULT_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    REQUEST_TIMEOUT: int = 15
    MAX_CONCURRENT_SCRAPES: int = 5
    
    # Currency conversions (Base: THB ฿)
    DEFAULT_CURRENCY: str = "THB"
    CURRENCY_RATES: dict = {
        "THB": 1.0,
        "USD": 0.028,
        "EUR": 0.026,
        "GBP": 0.022,
        "SGD": 0.038,
        "JPY": 4.35,
    }
    
    # Categories of IT Equipment
    CATEGORIES: list = [
        "Graphics Cards (GPU)",
        "Processors (CPU)",
        "Laptops & Notebooks",
        "Memory (RAM)",
        "Storage (SSD & HDD)",
        "Monitors & Displays",
        "Motherboards",
        "Power Supplies (PSU)",
        "PC Cases & Cooling",
        "Gaming Peripherals"
    ]

settings = Settings()
