import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.auth.routes import router as auth_router
from backend.config import settings
from backend.middleware.logging_mw import RequestLoggingMiddleware
from backend.middleware.tenant import TenantMiddleware
from backend.modules.advertising.routes import router as ads_router
from backend.modules.analytics.routes import router as analytics_router
from backend.modules.commerce.routes import router as commerce_router
from backend.modules.connect.routes import router as connect_router
from backend.modules.content.routes import router as content_router
from backend.modules.creators.routes import router as creators_router
from backend.modules.intelligence.routes import router as intelligence_router
from backend.modules.live.routes import router as live_router
from backend.modules.webhooks.routes import router as webhooks_router

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Frodo - Unified TikTok Platform",
        description="Single SaaS dashboard for managing TikTok Shop, Ads, Content, and Creators",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Middleware (order matters: last added = first executed)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(TenantMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routes
    api_prefix = "/api"
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(connect_router, prefix=api_prefix)
    app.include_router(commerce_router, prefix=api_prefix)
    app.include_router(ads_router, prefix=api_prefix)
    app.include_router(content_router, prefix=api_prefix)
    app.include_router(creators_router, prefix=api_prefix)
    app.include_router(intelligence_router, prefix=api_prefix)
    app.include_router(live_router, prefix=api_prefix)
    app.include_router(analytics_router, prefix=api_prefix)

    # Webhooks at root (no /api prefix - external callbacks)
    app.include_router(webhooks_router)

    @app.get("/health")
    async def health_check() -> dict:
        return {"status": "healthy", "version": "0.1.0"}

    return app


app = create_app()
