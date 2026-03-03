from typing import Any

from backend.db.models.platform import Platform
from backend.tiktok.circuit_breaker import CircuitBreaker, CircuitBreakerOpen
from backend.tiktok.developer.client import TikTokDeveloperClient
from backend.tiktok.live.client import TikTokLiveClientWrapper
from backend.tiktok.marketing.client import TikTokMarketingClient
from backend.tiktok.rate_limiter import (
    developer_rate_limiter,
    live_rate_limiter,
    marketing_rate_limiter,
    research_rate_limiter,
    shop_rate_limiter,
)
from backend.tiktok.research.client import TikTokResearchClient
from backend.tiktok.retry import with_retry
from backend.tiktok.shop.client import TikTokShopClient
from backend.tiktok.shop.sdk_client import TikTokShopSDKClient

# Per-platform circuit breakers
_circuit_breakers: dict[Platform, CircuitBreaker] = {
    Platform.SHOP: CircuitBreaker(),
    Platform.DEVELOPER: CircuitBreaker(),
    Platform.MARKETING: CircuitBreaker(),
    Platform.LIVE: CircuitBreaker(),
    Platform.RESEARCH: CircuitBreaker(),
}

_rate_limiters = {
    Platform.SHOP: shop_rate_limiter,
    Platform.DEVELOPER: developer_rate_limiter,
    Platform.MARKETING: marketing_rate_limiter,
    Platform.LIVE: live_rate_limiter,
    Platform.RESEARCH: research_rate_limiter,
}

# Type alias for all supported client types
PlatformClient = (
    TikTokShopClient
    | TikTokShopSDKClient
    | TikTokDeveloperClient
    | TikTokMarketingClient
    | TikTokResearchClient
    | TikTokLiveClientWrapper
)


class PlatformGateway:
    """Unified gateway for all TikTok platform API calls.

    Wraps each call with rate limiting, circuit breaker, and retry logic.
    """

    def __init__(
        self,
        platform: Platform,
        account_id: str,
        client: PlatformClient,
    ) -> None:
        self._platform = platform
        self._account_id = account_id
        self._client = client
        self._circuit_breaker = _circuit_breakers[platform]
        self._rate_limiter = _rate_limiters[platform]

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a platform API request through the middleware chain."""
        if not self._circuit_breaker.allow_request():
            raise CircuitBreakerOpen(f"Circuit breaker open for {self._platform.value}")

        allowed = await self._rate_limiter.acquire(self._account_id)
        if not allowed:
            raise RateLimitExceeded(
                f"Rate limit exceeded for {self._platform.value} account {self._account_id}"
            )

        try:
            result = await with_retry(
                self._client.request,
                method,
                path,
                params=params,
                json_body=json_body,
            )
            self._circuit_breaker.record_success()
            return result
        except Exception:
            self._circuit_breaker.record_failure()
            raise

    async def get(
        self, path: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        return await self.request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return await self.request("POST", path, params=params, json_body=json_body)


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded for a platform account."""
