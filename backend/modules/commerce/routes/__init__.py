from fastapi import APIRouter

from backend.modules.commerce.routes.affiliate import router as affiliate_router
from backend.modules.commerce.routes.analytics import router as analytics_router
from backend.modules.commerce.routes.customer_service import (
    router as customer_service_router,
)
from backend.modules.commerce.routes.finance import router as finance_router
from backend.modules.commerce.routes.fulfillment import router as fulfillment_router
from backend.modules.commerce.routes.logistics import router as logistics_router
from backend.modules.commerce.routes.orders import router as orders_router
from backend.modules.commerce.routes.products import router as products_router
from backend.modules.commerce.routes.promotions import router as promotions_router
from backend.modules.commerce.routes.returns import router as returns_router
from backend.modules.commerce.routes.shops import router as shops_router
from backend.modules.commerce.routes.ws import router as ws_router

router = APIRouter(prefix="/commerce", tags=["commerce"])

router.include_router(shops_router)
router.include_router(products_router)
router.include_router(orders_router)
router.include_router(fulfillment_router)
router.include_router(returns_router)
router.include_router(analytics_router)
router.include_router(affiliate_router)
router.include_router(promotions_router)
router.include_router(finance_router)
router.include_router(customer_service_router)
router.include_router(logistics_router)
router.include_router(ws_router)
