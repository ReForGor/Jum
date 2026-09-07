import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.config import settings
from app.database import init_db, get_db, AsyncSessionLocal
from app.seed_data import seed_initial_data
from app.models.product import Product
from app.models.store import Store
from app.models.price_listing import PriceListing
from app.auth import get_current_user_optional
from app.api import (
    products_router,
    compare_router,
    search_router,
    history_router,
    scrapers_router,
    alerts_router,
    export_router,
    auth_router,
    notifications_router,
    admin_router
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("techprice")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    async with AsyncSessionLocal() as session:
        logger.info("Seeding initial Thai IT equipment platforms (JIB, iHaveCPU, BaNANA, Advice)...")
        await seed_initial_data(session)
    logger.info("TechPrice Thai IT Aggregation Engine initialized and ready!")
    yield
    logger.info("Shutting down TechPrice Engine.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static & Templates
app.mount("/static", StaticFiles(directory=f"{settings.BASE_DIR}/app/static"), name="static")
templates = Jinja2Templates(directory=f"{settings.BASE_DIR}/app/templates")

# Include API routers
app.include_router(products_router)
app.include_router(compare_router)
app.include_router(search_router)
app.include_router(history_router)
app.include_router(scrapers_router)
app.include_router(alerts_router)
app.include_router(export_router)
app.include_router(auth_router)
app.include_router(notifications_router)
app.include_router(admin_router)

# ----------------- UI Web Pages -----------------

@app.get("/", include_in_schema=False)
async def home_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    prod_count = (await db.execute(select(func.count(Product.id)))).scalar() or 0
    store_count = (await db.execute(select(func.count(Store.id)))).scalar() or 0
    listing_count = (await db.execute(select(func.count(PriceListing.id)))).scalar() or 0

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "categories": settings.CATEGORIES,
            "prod_count": prod_count,
            "store_count": store_count,
            "listing_count": listing_count,
            "currencies": settings.CURRENCY_RATES,
            "user": current_user
        }
    )

@app.get("/compare", include_in_schema=False)
async def compare_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    products_res = await db.execute(select(Product.id, Product.name, Product.category, Product.image_url, Product.msrp))
    all_prods = products_res.all()
    return templates.TemplateResponse(
        request=request,
        name="compare.html",
        context={
            "products": all_prods,
            "user": current_user
        }
    )

@app.get("/deals", include_in_schema=False)
async def deals_page(
    request: Request,
    current_user = Depends(get_current_user_optional)
):
    return templates.TemplateResponse(
        request=request,
        name="deals.html",
        context={
            "categories": settings.CATEGORIES,
            "user": current_user
        }
    )

@app.get("/watchlist", include_in_schema=False)
async def watchlist_page(
    request: Request,
    current_user = Depends(get_current_user_optional)
):
    return templates.TemplateResponse(
        request=request,
        name="watchlist.html",
        context={
            "user": current_user
        }
    )

@app.get("/platforms", include_in_schema=False)
async def platforms_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    stores_res = await db.execute(select(Store))
    stores = stores_res.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="platforms.html",
        context={
            "stores": stores,
            "user": current_user
        }
    )

@app.get("/api-explorer", include_in_schema=False)
async def api_docs_page(
    request: Request,
    current_user = Depends(get_current_user_optional)
):
    return templates.TemplateResponse(
        request=request,
        name="api_docs.html",
        context={
            "user": current_user
        }
    )

@app.get("/admin", include_in_schema=False)
async def admin_page(
    request: Request,
    current_user = Depends(get_current_user_optional)
):
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "user": current_user,
            "categories": settings.CATEGORIES
        }
    )
