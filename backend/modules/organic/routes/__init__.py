from fastapi import APIRouter

from backend.modules.organic.routes.accounts import router as accounts_router
from backend.modules.organic.routes.mentions import router as mentions_router

router = APIRouter(prefix="/organic", tags=["organic"])
router.include_router(accounts_router)
router.include_router(mentions_router)
