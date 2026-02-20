from fastapi import APIRouter

from backend.modules.creators.routes_campaigns import router as campaigns_router
from backend.modules.creators.routes_discovery import router as discovery_router
from backend.modules.creators.routes_profiles import router as profiles_router
from backend.modules.creators.routes_spark_ads import router as spark_ads_router

router = APIRouter(prefix="/creators", tags=["creators"])

router.include_router(profiles_router)
router.include_router(discovery_router)
router.include_router(campaigns_router)
router.include_router(spark_ads_router)
