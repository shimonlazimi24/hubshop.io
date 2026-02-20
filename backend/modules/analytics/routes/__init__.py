from fastapi import APIRouter

from backend.modules.analytics.routes.api_keys import router as api_keys_router
from backend.modules.analytics.routes.notifications import (
    router as notifications_router,
)
from backend.modules.analytics.routes.overview import router as overview_router
from backend.modules.analytics.routes.reports import router as reports_router

router = APIRouter(prefix="/analytics", tags=["analytics"])

router.include_router(overview_router)
router.include_router(reports_router)
router.include_router(notifications_router)
router.include_router(api_keys_router)
