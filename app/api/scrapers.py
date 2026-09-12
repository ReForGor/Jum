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
    from app.api.products import clear_products_cache
    from app.api.history import clear_history_cache
    clear_products_cache()
    clear_history_cache()
    return result

from app.services.scheduler import scheduler

@router.get("/scheduler")
async def get_scheduler_status():
    return scheduler.get_status()

@router.post("/scheduler/trigger")
async def trigger_scheduler_job(background_tasks: BackgroundTasks):
    background_tasks.add_task(scheduler.execute_scrape_job, False)
    return {"message": "Daily live scrape job triggered in background", "simulate": False}

@router.get("/last-job")
async def get_last_job():
    if not scraper_manager.last_job_result:
        return {"status": "No jobs executed recently"}
    return scraper_manager.last_job_result
