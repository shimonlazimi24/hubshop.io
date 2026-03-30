from fastapi import APIRouter

from backend.modules.gmvmax.routes.workflow_routes import router as workflow_router

router = APIRouter(prefix="/gmvmax", tags=["gmvmax"])

router.include_router(workflow_router)
