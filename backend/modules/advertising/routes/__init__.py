from fastapi import APIRouter

from backend.modules.advertising.routes.accounts import router as accounts_router
from backend.modules.advertising.routes.ad_groups import router as ad_groups_router
from backend.modules.advertising.routes.ads import router as ads_router
from backend.modules.advertising.routes.audiences import router as audiences_router
from backend.modules.advertising.routes.automation import router as automation_router
from backend.modules.advertising.routes.campaigns import router as campaigns_router
from backend.modules.advertising.routes.catalogs import router as catalogs_router
from backend.modules.advertising.routes.comments import router as comments_router
from backend.modules.advertising.routes.creatives import router as creatives_router
from backend.modules.advertising.routes.pixels import router as pixels_router
from backend.modules.advertising.routes.reports import router as reports_router
from backend.modules.advertising.routes.change_log import router as change_log_router
from backend.modules.advertising.routes.custom_conversions import (
    router as custom_conversions_router,
)
from backend.modules.advertising.routes.identities import router as identities_router
from backend.modules.advertising.routes.leads import router as leads_router
from backend.modules.advertising.routes.search import router as search_router
from backend.modules.advertising.routes.split_tests import router as split_tests_router
from backend.modules.advertising.routes.symphony import router as symphony_router

router = APIRouter(prefix="/ads", tags=["advertising"])

router.include_router(accounts_router)
router.include_router(campaigns_router)
router.include_router(ad_groups_router)
router.include_router(ads_router)
router.include_router(reports_router)
router.include_router(audiences_router)
router.include_router(pixels_router)
router.include_router(catalogs_router)
router.include_router(creatives_router)
router.include_router(automation_router)
router.include_router(comments_router)
router.include_router(search_router)
router.include_router(symphony_router)
router.include_router(split_tests_router)
router.include_router(leads_router)
router.include_router(identities_router)
router.include_router(change_log_router)
router.include_router(custom_conversions_router)
