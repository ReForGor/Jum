from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, AsyncSessionLocal
from app.scrapers.manager import scraper_manager
from app.schemas.scraper import ScraperRunRequest, ScrapeJobResult, ScraperPlatformStatus

router = APIRouter(prefix="/api/scrapers", tags=["Scrapers"])

@router.get("/status", response_model=List[ScraperPlatformStatus])
async def get_scrapers_status(db: AsyncSession = Depends(get_db)):
    return await scraper_manager.get_platform_statuses(db)

@router.post("/run", response_model=ScrapeJobResult)
async def run_scraper_job(
    req: ScraperRunRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await scraper_manager.run_scrape(
        db=db,
        platform_slug=req.platform_slug,
        product_id=req.product_id,
        simulate=req.simulate_live
    )
    return result

@router.get("/last-job")
async def get_last_job():
    if not scraper_manager.last_job_result:
        return {"status": "No jobs executed recently"}
    return scraper_manager.last_job_result
