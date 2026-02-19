from fastapi import APIRouter

from backend.modules.commerce.routes.analytics import router as analytics_router
from backend.modules.commerce.routes.fulfillment import router as fulfillment_router
from backend.modules.commerce.routes.orders import router as orders_router
from backend.modules.commerce.routes.products import router as products_router
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
router.include_router(ws_router)
