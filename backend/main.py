import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.auth.routes import router as auth_router
from backend.config import settings
from backend.middleware.logging_mw import RequestLoggingMiddleware
from backend.middleware.tenant import TenantMiddleware
from backend.modules.advertising.routes import router as ads_router
from backend.modules.analytics.routes import router as analytics_router
from backend.modules.commerce.routes import router as commerce_router
from backend.modules.connect.routes import router as connect_router
from backend.modules.connect.sync_routes import router as sync_router
from backend.modules.connect.ws import router as connect_ws_router
from backend.modules.content.routes import router as content_router
from backend.modules.creators.routes import router as creators_router
from backend.modules.customer_engagement.routes import router as engagement_router
from backend.modules.gmvmax.routes import router as gmvmax_router
from backend.modules.intelligence.routes import router as intelligence_router
from backend.modules.live.routes import router as live_router
from backend.modules.messaging.routes import router as messaging_router
from backend.modules.organic.routes import router as organic_router
from backend.modules.webhooks.routes import router as webhooks_router


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add standard security headers to every response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response


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
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Workspace-Id",
            "X-Requested-With",
        ],
    )

    # API routes
    api_prefix = "/api"
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(connect_router, prefix=api_prefix)
    app.include_router(sync_router, prefix=api_prefix)
    app.include_router(connect_ws_router, prefix=api_prefix)
    app.include_router(commerce_router, prefix=api_prefix)
    app.include_router(ads_router, prefix=api_prefix)
    app.include_router(content_router, prefix=api_prefix)
    app.include_router(creators_router, prefix=api_prefix)
    app.include_router(engagement_router, prefix=api_prefix)
    app.include_router(gmvmax_router, prefix=api_prefix)
    app.include_router(intelligence_router, prefix=api_prefix)
    app.include_router(live_router, prefix=api_prefix)
    app.include_router(messaging_router, prefix=api_prefix)
    app.include_router(organic_router, prefix=api_prefix)
    app.include_router(analytics_router, prefix=api_prefix)

    # Shop Health module
    from backend.modules.shop_health.routes import router as shop_health_router

    app.include_router(shop_health_router, prefix=api_prefix)

    # Webhooks at root (no /api prefix - external callbacks)
    app.include_router(webhooks_router)

    @app.get("/health")
    async def health_check() -> dict:
        import redis.asyncio as aioredis
        from sqlalchemy import text

        from backend.db.engine import async_session_factory

        checks: dict[str, str] = {"status": "healthy", "version": "0.1.0"}

        # Database connectivity
        try:
            async with async_session_factory() as session:
                await session.execute(text("SELECT 1"))
            checks["database"] = "connected"
        except Exception:
            checks["database"] = "disconnected"
            checks["status"] = "degraded"

        # Redis connectivity
        try:
            r = aioredis.from_url(settings.redis_url, decode_responses=True)
            await r.ping()
            await r.aclose()
            checks["redis"] = "connected"
        except Exception:
            checks["redis"] = "disconnected"
            checks["status"] = "degraded"

        return checks

    return app


app = create_app()
