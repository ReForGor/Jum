import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from app.database import AsyncSessionLocal
from app.scrapers.manager import scraper_manager

logger = logging.getLogger("techprice.scheduler")

# Asia/Bangkok is UTC+7
BANGKOK_TZ = timezone(timedelta(hours=7))

class DailyScrapeScheduler:
    def __init__(self):
        self.is_active: bool = True
        self.is_running_job: bool = False
        self.last_run_time: Optional[datetime] = None
        self.next_run_time: Optional[datetime] = None
        self.last_result: Optional[Dict[str, Any]] = None
        self._task: Optional[asyncio.Task] = None

    def calculate_next_run(self, target_hour: int = 4, target_minute: int = 30, jitter_minutes: int = 30) -> tuple[datetime, float]:
        """
        Calculate next run time between 04:30 and 05:00 AM (Bangkok Time, UTC+7).
        Returns: (target_datetime_bangkok, seconds_to_wait)
        """
        now_bkk = datetime.now(BANGKOK_TZ)
        jitter_seconds = random.randint(0, jitter_minutes * 60)
        target_today = now_bkk.replace(
            hour=target_hour,
            minute=target_minute,
            second=0,
            microsecond=0
        ) + timedelta(seconds=jitter_seconds)

        if now_bkk >= target_today:
            # Already passed today, schedule for tomorrow
            target_next = target_today + timedelta(days=1)
        else:
            target_next = target_today

        seconds_until = max(1.0, (target_next - now_bkk).total_seconds())
        return target_next, seconds_until

    async def execute_scrape_job(self, simulate: bool = False) -> Dict[str, Any]:
        """
        Runs the daily scrape job across all products and Thai stores.
        """
        if self.is_running_job:
            logger.warning("[Scheduler] Scrape job is already running, skipping overlapping invocation.")
            return {"status": "skipped", "reason": "already_running"}

        self.is_running_job = True
        started_at = datetime.now(BANGKOK_TZ)
        logger.info(f"🚀 [Scheduler] Starting daily price sync at {started_at.strftime('%Y-%m-%d %H:%M:%S %Z')} (simulate={simulate})")

        try:
            async with AsyncSessionLocal() as session:
                result = await scraper_manager.run_scrape(
                    db=session,
                    platform_slug=None,
                    product_id=None,
                    simulate=simulate
                )
                self.last_run_time = datetime.now(BANGKOK_TZ)
                self.last_result = result
                logger.info(
                    f"✅ [Scheduler] Daily price sync completed successfully: "
                    f"scraped={result.get('items_scraped')}, updated={result.get('prices_updated')}, "
                    f"alerts={result.get('triggered_alerts')}"
                )
                return result
        except Exception as e:
            logger.error(f"❌ [Scheduler] Error during daily scrape job: {e}", exc_info=True)
            self.last_result = {"status": "error", "error": str(e)}
            return self.last_result
        finally:
            self.is_running_job = False

    async def run_loop(self):
        """
        Infinite background worker loop: waits until 04:30 - 05:00 AM Bangkok Time every day.
        """
        logger.info("⏰ [Scheduler] Daily 04:30-05:00 AM Automated Scraper background worker started.")
        while self.is_active:
            try:
                next_dt, wait_secs = self.calculate_next_run(target_hour=4, target_minute=30, jitter_minutes=30)
                self.next_run_time = next_dt
                hours = wait_secs / 3600
                logger.info(f"⏳ [Scheduler] Next scheduled live price scrape: {next_dt.strftime('%Y-%m-%d %H:%M:%S %Z')} (in {hours:.2f} hours)")

                await asyncio.sleep(wait_secs)

                if not self.is_active:
                    break

                logger.info("🌅 [Scheduler] Daily morning window (04:30-05:00) reached. Triggering live store price sync...")
                await self.execute_scrape_job(simulate=False)

            except asyncio.CancelledError:
                logger.info("[Scheduler] Scheduler task cancelled.")
                break
            except Exception as e:
                logger.error(f"[Scheduler] Unexpected loop error: {e}", exc_info=True)
                await asyncio.sleep(60)

    def start(self) -> asyncio.Task:
        self.is_active = True
        self._task = asyncio.create_task(self.run_loop())
        return self._task

    def stop(self):
        self.is_active = False
        if self._task and not self._task.done():
            self._task.cancel()

    def get_status(self) -> Dict[str, Any]:
        return {
            "scheduler_active": self.is_active,
            "is_running_job": self.is_running_job,
            "schedule_window": "04:30 - 05:00 AM (Asia/Bangkok / UTC+7)",
            "next_run_time": self.next_run_time.strftime("%Y-%m-%d %H:%M:%S %Z") if self.next_run_time else None,
            "last_run_time": self.last_run_time.strftime("%Y-%m-%d %H:%M:%S %Z") if self.last_run_time else None,
            "last_result": self.last_result
        }

scheduler = DailyScrapeScheduler()

