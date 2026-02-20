from fastapi import APIRouter

from backend.modules.advertising.routes.accounts import router as accounts_router
from backend.modules.advertising.routes.ad_groups import router as ad_groups_router
from backend.modules.advertising.routes.ads import router as ads_router
from backend.modules.advertising.routes.audiences import router as audiences_router
from backend.modules.advertising.routes.campaigns import router as campaigns_router
from backend.modules.advertising.routes.catalogs import router as catalogs_router
from backend.modules.advertising.routes.pixels import router as pixels_router
from backend.modules.advertising.routes.reports import router as reports_router

router = APIRouter(prefix="/ads", tags=["advertising"])

router.include_router(accounts_router)
router.include_router(campaigns_router)
router.include_router(ad_groups_router)
router.include_router(ads_router)
router.include_router(reports_router)
router.include_router(audiences_router)
router.include_router(pixels_router)
router.include_router(catalogs_router)
