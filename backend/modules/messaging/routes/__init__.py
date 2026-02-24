from fastapi import APIRouter

from backend.modules.messaging.routes.auto_messages import (
    router as auto_messages_router,
)
from backend.modules.messaging.routes.conversations import (
    router as conversations_router,
)

router = APIRouter(prefix="/messaging", tags=["messaging"])
router.include_router(conversations_router)
router.include_router(auto_messages_router)
