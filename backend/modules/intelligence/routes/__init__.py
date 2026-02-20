from fastapi import APIRouter

from backend.modules.intelligence.routes.competitors import router as competitors_router
from backend.modules.intelligence.routes.creators import router as creators_router
from backend.modules.intelligence.routes.sources import router as sources_router
from backend.modules.intelligence.routes.trends import router as trends_router

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

router.include_router(trends_router)
router.include_router(competitors_router)
router.include_router(creators_router)
router.include_router(sources_router)
