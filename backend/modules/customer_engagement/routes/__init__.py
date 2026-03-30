from fastapi import APIRouter

from backend.modules.customer_engagement.routes.engagement_routes import (
    router as engagement_routes_router,
)

router = APIRouter(prefix="/engagement", tags=["engagement"])

router.include_router(engagement_routes_router)
