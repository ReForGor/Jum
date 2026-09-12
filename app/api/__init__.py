from app.api.products import router as products_router
from app.api.compare import router as compare_router
from app.api.search import router as search_router
from app.api.history import router as history_router
from app.api.scrapers import router as scrapers_router
from app.api.alerts import router as alerts_router
from app.api.export import router as export_router
from app.api.auth import router as auth_router
from app.api.notifications import router as notifications_router
from app.api.admin import router as admin_router
from app.api.emails import router as emails_router

__all__ = [
    "products_router",
    "compare_router",
    "search_router",
    "history_router",
    "scrapers_router",
    "alerts_router",
    "export_router",
    "auth_router",
    "notifications_router",
    "admin_router",
    "emails_router"
]
