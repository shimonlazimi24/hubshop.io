from fastapi import APIRouter

from backend.modules.live.routes.analytics import router as analytics_router
from backend.modules.live.routes.sessions import router as sessions_router

router = APIRouter(prefix="/live", tags=["live"])

router.include_router(sessions_router)
router.include_router(analytics_router)
