from fastapi import APIRouter

from backend.modules.content.routes.bridge import router as bridge_router
from backend.modules.content.routes.calendar import router as calendar_router
from backend.modules.content.routes.commercial import router as commercial_router
from backend.modules.content.routes.comments import router as comments_router
from backend.modules.content.routes.publish import router as publish_router
from backend.modules.content.routes.videos import router as videos_router

router = APIRouter(prefix="/content", tags=["content"])

router.include_router(videos_router)
router.include_router(publish_router)
router.include_router(calendar_router)
router.include_router(comments_router)
router.include_router(commercial_router)
router.include_router(bridge_router)
