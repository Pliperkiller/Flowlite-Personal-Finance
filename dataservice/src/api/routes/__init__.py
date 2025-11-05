from .transactions import router as transactions_router
from .insights import router as insights_router
from .catalogs import router as catalogs_router
from .health import router as health_router
from .dashboard import router as dashboard_router

__all__ = [
    "transactions_router",
    "insights_router",
    "catalogs_router",
    "health_router",
    "dashboard_router",
]
