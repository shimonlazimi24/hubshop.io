# TikTok Shop SDK Sidecar Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Run the official TikTok Shop Node.js SDK as a Fastify sidecar inside Docker Compose, exposing all 202 operations via a generic REST proxy, then migrate the Python backend to use it.

**Architecture:** Stateless Fastify server dynamically resolves SDK API classes from URL params (domain/version/operation). Python backend calls it via httpx through the existing PlatformGateway middleware (circuit breaker, rate limiter, retry).

**Tech Stack:** Node.js 20 / Fastify / TypeScript / Official TikTok Shop SDK / Docker / Python httpx

---

## Task 1: Scaffold the Node.js Sidecar Project

**Files:**
- Create: `tiktok-shop-sdk/package.json`
- Create: `tiktok-shop-sdk/tsconfig.json`
- Create: `tiktok-shop-sdk/.gitignore`

**Step 1: Create project directory**

```bash
mkdir -p tiktok-shop-sdk/src
```

**Step 2: Create package.json**

```json
{
  "name": "tiktok-shop-sdk-sidecar",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts"
  },
  "dependencies": {
    "fastify": "^5.2.0",
    "request": "2.88.2",
    "uuid": "^11.0.0"
  },
  "devDependencies": {
    "@types/request": "2.48.12",
    "@types/node": "20",
    "@types/uuid": "^10.0.0",
    "tslib": "2.6.2",
    "typescript": "^5.4.0",
    "ts-node": "^10.9.0"
  }
}
```

**Step 3: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": ".",
    "strict": false,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*", "sdk/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**Step 4: Create .gitignore**

```
node_modules/
dist/
*.js.map
```

**Step 5: Copy the official SDK into the sidecar**

```bash
cp -r /tmp/tiktok-shop-sdk/api tiktok-shop-sdk/sdk/api
cp -r /tmp/tiktok-shop-sdk/client tiktok-shop-sdk/sdk/client
cp -r /tmp/tiktok-shop-sdk/model tiktok-shop-sdk/sdk/model
cp -r /tmp/tiktok-shop-sdk/utils tiktok-shop-sdk/sdk/utils
cp /tmp/tiktok-shop-sdk/api.ts tiktok-shop-sdk/sdk/api.ts
cp /tmp/tiktok-shop-sdk/index.ts tiktok-shop-sdk/sdk/index.ts
```

**Step 6: Install dependencies**

```bash
cd tiktok-shop-sdk && npm install
```

**Step 7: Commit**

```bash
git add tiktok-shop-sdk/package.json tiktok-shop-sdk/tsconfig.json tiktok-shop-sdk/.gitignore tiktok-shop-sdk/sdk/
git commit -m "chore: scaffold tiktok-shop-sdk sidecar with official SDK"
```

---

## Task 2: Build the SDK Registry

**Files:**
- Create: `tiktok-shop-sdk/src/sdk-registry.ts`

The registry maps `(domain, version)` → SDK API class dynamically from `API_OBJECT`.

**Step 1: Create sdk-registry.ts**

```typescript
import { API_OBJECT } from "../sdk/api/apis";

/**
 * Build a lookup map: { "product_V202502": ProductV202502Api instance, ... }
 * from the SDK's API_OBJECT. Domain is lowercased for case-insensitive matching.
 */

type ApiInstance = InstanceType<(typeof API_OBJECT)[keyof typeof API_OBJECT]>;

interface RegistryEntry {
  instance: ApiInstance;
  methods: string[];
}

let registry: Map<string, RegistryEntry> | null = null;

function buildKey(domain: string, version: string): string {
  return `${domain.toLowerCase()}_${version}`;
}

/**
 * Parse an API class name like "ProductV202502Api" into { domain: "product", version: "V202502" }
 */
function parseApiClassName(name: string): { domain: string; version: string } | null {
  const match = name.match(/^([A-Za-z]+?)(V\d{6})Api$/);
  if (!match) return null;
  return { domain: match[1].toLowerCase(), version: match[2] };
}

export function getRegistry(basePath?: string): Map<string, RegistryEntry> {
  if (registry) return registry;

  registry = new Map();

  for (const [apiName, ApiClass] of Object.entries(API_OBJECT)) {
    const parsed = parseApiClassName(apiName);
    if (!parsed) continue;

    const instance = new (ApiClass as any)(basePath) as ApiInstance;
    const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(instance))
      .filter((m) => m !== "constructor" && !m.startsWith("_") && !m.startsWith("set") && !m.startsWith("get") && !m.startsWith("add") && typeof (instance as any)[m] === "function");

    const key = buildKey(parsed.domain, parsed.version);
    registry.set(key, { instance, methods });
  }

  return registry;
}

export function resolveOperation(
  domain: string,
  version: string,
  operation: string,
  basePath?: string,
): { instance: ApiInstance; method: Function } | null {
  const reg = getRegistry(basePath);
  const key = buildKey(domain, version);
  const entry = reg.get(key);
  if (!entry) return null;

  const method = (entry.instance as any)[operation];
  if (typeof method !== "function") return null;

  return { instance: entry.instance, method: method.bind(entry.instance) };
}

export function listOperations(basePath?: string): Array<{
  domain: string;
  version: string;
  operations: string[];
}> {
  const reg = getRegistry(basePath);
  const result: Array<{ domain: string; version: string; operations: string[] }> = [];

  for (const [key, entry] of reg.entries()) {
    const [domain, version] = key.split("_");
    result.push({ domain, version, operations: entry.methods });
  }

  return result.sort((a, b) => a.domain.localeCompare(b.domain) || a.version.localeCompare(b.version));
}
```

**Step 2: Verify it compiles**

```bash
cd tiktok-shop-sdk && npx tsc --noEmit src/sdk-registry.ts
```

**Step 3: Commit**

```bash
git add tiktok-shop-sdk/src/sdk-registry.ts
git commit -m "feat(sdk-sidecar): add SDK registry for dynamic operation resolution"
```

---

## Task 3: Build the Fastify Server + Dynamic Router

**Files:**
- Create: `tiktok-shop-sdk/src/index.ts`
- Create: `tiktok-shop-sdk/src/router.ts`

**Step 1: Create router.ts**

```typescript
import { FastifyInstance, FastifyRequest, FastifyReply } from "fastify";
import { v4 as uuidv4 } from "uuid";
import { resolveOperation, listOperations } from "./sdk-registry";
import { ClientConfiguration } from "../sdk/client/config";

interface ShopRequestBody {
  access_token: string;
  shop_cipher?: string;
  params?: Record<string, any>;
  body?: Record<string, any>;
}

interface ShopRouteParams {
  domain: string;
  version: string;
  operation: string;
}

export function registerRoutes(app: FastifyInstance): void {
  // Discovery endpoint
  app.get("/api/shop/operations", async (_req, reply) => {
    const operations = listOperations();
    reply.send({ success: true, data: operations });
  });

  // Generic operation proxy
  app.post<{ Params: ShopRouteParams; Body: ShopRequestBody }>(
    "/api/shop/:domain/:version/:operation",
    async (request, reply) => {
      const requestId = uuidv4();
      const { domain, version, operation } = request.params;
      const { access_token, shop_cipher, params = {}, body: reqBody } = request.body;

      if (!access_token) {
        reply.status(400).send({
          success: false,
          error: { code: "MISSING_ACCESS_TOKEN", message: "access_token is required" },
          request_id: requestId,
        });
        return;
      }

      const resolved = resolveOperation(domain, version, operation);
      if (!resolved) {
        reply.status(404).send({
          success: false,
          error: {
            code: "INVALID_OPERATION",
            message: `Operation '${operation}' not found on ${domain}${version}Api`,
          },
          request_id: requestId,
        });
        return;
      }

      try {
        // Build args array from params + body.
        // SDK methods follow the pattern:
        //   method(requiredParam1, xTtsAccessToken, contentType, optionalParam1, shopCipher?, requestBody?, options?)
        // We use a generic approach: pass all params in order with access_token and shop_cipher injected.
        const methodParams = params || {};
        const callArgs: any[] = [];

        // Most SDK methods expect positional args. We pass them via a named object approach
        // by calling through the underlying request mechanism.
        // The simplest reliable approach: call the method with spread args from params array.
        if (methodParams._args) {
          // Explicit ordered args mode
          callArgs.push(...methodParams._args);
        } else {
          // Auto-build: inject access_token as x-tts-access-token header, shop_cipher as query param
          // For generic passthrough, we use the SDK's interceptor which handles signing.
          // We just need to set the access_token header on the request.
          const headerOpts = {
            headers: {
              "x-tts-access-token": access_token,
              ...(shop_cipher ? {} : {}),
            },
          };

          // Build ordered args from common SDK method signature patterns
          // Most methods: (requiredParams..., xTtsAccessToken, contentType, optionalParams..., shopCipher?, body?, options?)
          // We use a simplified call: pass known positional args
          const orderedArgs = buildOrderedArgs(methodParams, access_token, shop_cipher, reqBody);
          callArgs.push(...orderedArgs, headerOpts);
        }

        const result = await resolved.method(...callArgs);

        reply.send({
          success: true,
          data: result.body || result,
          request_id: requestId,
        });
      } catch (err: any) {
        const statusCode = err.statusCode || err.response?.statusCode || 500;
        reply.status(statusCode).send({
          success: false,
          error: {
            code: "SDK_ERROR",
            message: err.message || "Unknown SDK error",
            details: err.body || err.response?.body || null,
          },
          request_id: requestId,
        });
      }
    }
  );
}

/**
 * Build ordered positional args for SDK method calls.
 * SDK methods generated by OpenAPI follow patterns like:
 *   method(pageSize, xTtsAccessToken, contentType, pageToken?, shopCipher?, body?)
 * We extract named params and arrange them.
 */
function buildOrderedArgs(
  params: Record<string, any>,
  accessToken: string,
  shopCipher?: string,
  body?: Record<string, any>,
): any[] {
  const args: any[] = [];

  // Extract known positional params (order matters for SDK methods)
  // Remove meta-params, push the rest as positional
  const { contentType, ...restParams } = params;

  // Push all explicit params first
  for (const value of Object.values(restParams)) {
    args.push(value);
  }

  // Then access_token (always required by SDK methods as x-tts-access-token)
  args.push(accessToken);

  // Content type (default application/json)
  args.push(contentType || "application/json");

  // Optional params that go at the end: page tokens, shop_cipher, body
  // These are often undefined/optional — SDK handles undefined gracefully
  if (shopCipher) args.push(shopCipher);
  if (body) args.push(body);

  return args;
}
```

**Step 2: Create index.ts (server entry)**

```typescript
import Fastify from "fastify";
import { registerRoutes } from "./router";
import { ClientConfiguration } from "../sdk/client/config";

const app = Fastify({ logger: true });

// Configure SDK with app credentials from env
const appKey = process.env.TIKTOK_SHOP_APP_KEY;
const appSecret = process.env.TIKTOK_SHOP_APP_SECRET;

if (!appKey || !appSecret) {
  console.error("TIKTOK_SHOP_APP_KEY and TIKTOK_SHOP_APP_SECRET must be set");
  process.exit(1);
}

ClientConfiguration.globalConfig.app_key = appKey;
ClientConfiguration.globalConfig.app_secret = appSecret;

// Health check
app.get("/health", async () => ({ status: "ok" }));

// Register shop API routes
registerRoutes(app);

const start = async () => {
  try {
    const port = parseInt(process.env.PORT || "3000", 10);
    await app.listen({ port, host: "0.0.0.0" });
    console.log(`TikTok Shop SDK sidecar listening on port ${port}`);
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();
```

**Step 3: Verify compilation**

```bash
cd tiktok-shop-sdk && npx tsc --noEmit
```

**Step 4: Commit**

```bash
git add tiktok-shop-sdk/src/
git commit -m "feat(sdk-sidecar): add Fastify server with dynamic operation router"
```

---

## Task 4: Dockerize the Sidecar

**Files:**
- Create: `tiktok-shop-sdk/Dockerfile`
- Create: `tiktok-shop-sdk/.dockerignore`

**Step 1: Create Dockerfile**

```dockerfile
FROM node:20-alpine

WORKDIR /app

RUN apk add --no-cache curl

COPY package.json package-lock.json* ./
RUN npm ci --omit=dev

COPY tsconfig.json ./
COPY sdk/ ./sdk/
COPY src/ ./src/

RUN npx tsc

EXPOSE 3000

CMD ["node", "dist/src/index.js"]
```

**Step 2: Create .dockerignore**

```
node_modules
dist
*.md
.git
```

**Step 3: Test Docker build**

```bash
cd tiktok-shop-sdk && docker build -t tiktok-shop-sdk:test .
```
Expected: Build succeeds, image created.

**Step 4: Commit**

```bash
git add tiktok-shop-sdk/Dockerfile tiktok-shop-sdk/.dockerignore
git commit -m "chore(sdk-sidecar): add Dockerfile for Node.js sidecar"
```

---

## Task 5: Add Sidecar to Docker Compose

**Files:**
- Modify: `docker-compose.yml` — add `tiktok-shop-sdk` service
- Modify: `.env` — add `TIKTOK_SHOP_SDK_URL`

**Step 1: Add service to docker-compose.yml**

Add after the `redis` service block:

```yaml
  tiktok-shop-sdk:
    build: ./tiktok-shop-sdk
    env_file: .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 15s
      timeout: 5s
      retries: 3
```

Add `tiktok-shop-sdk` to the `api` service `depends_on`:

```yaml
  api:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      tiktok-shop-sdk:
        condition: service_healthy
```

Also add to `celery-worker` depends_on:

```yaml
  celery-worker:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      tiktok-shop-sdk:
        condition: service_healthy
```

**Step 2: Add env var to .env**

```
TIKTOK_SHOP_SDK_URL=http://tiktok-shop-sdk:3000
```

**Step 3: Test docker compose build**

```bash
docker compose build tiktok-shop-sdk
```
Expected: Build succeeds.

**Step 4: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add tiktok-shop-sdk sidecar to Docker Compose"
```

---

## Task 6: Add SDK URL to Python Settings

**Files:**
- Modify: `backend/config.py:30` — add `tiktok_shop_sdk_url` setting

**Step 1: Add setting**

In `backend/config.py`, add after the `tiktok_shop_app_secret` line:

```python
    # TikTok Shop SDK Sidecar
    tiktok_shop_sdk_url: str = "http://localhost:3000"
```

**Step 2: Verify import still works**

```bash
python -c "from backend.config import settings; print(settings.tiktok_shop_sdk_url)"
```
Expected: `http://localhost:3000`

**Step 3: Commit**

```bash
git add backend/config.py
git commit -m "feat: add tiktok_shop_sdk_url to settings"
```

---

## Task 7: Write Tests for Python SDK Client

**Files:**
- Create: `tests/unit/tiktok/test_shop_sdk_client.py`

**Step 1: Write the failing tests**

```python
import pytest
import httpx
from unittest.mock import AsyncMock, patch

from backend.tiktok.shop.sdk_client import TikTokShopSDKClient


@pytest.mark.asyncio
async def test_sdk_client_call_success():
    """SDK client should POST to sidecar and return data."""
    mock_response = httpx.Response(
        200,
        json={
            "success": True,
            "data": {"products": [{"id": "123"}]},
            "request_id": "abc",
        },
    )

    with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_instance.aclose = AsyncMock()
        MockClient.return_value = mock_instance

        client = TikTokShopSDKClient(
            access_token="test_token",
            sdk_base_url="http://localhost:3000",
        )
        result = await client.call(
            "product", "V202502", "ProductsSearchPost",
            params={"pageSize": 50},
            body={"status": "LIVE"},
        )

        assert result == {"products": [{"id": "123"}]}
        mock_instance.post.assert_called_once()
        call_args = mock_instance.post.call_args
        assert "/api/shop/product/V202502/ProductsSearchPost" in call_args[0][0]
        await client.close()


@pytest.mark.asyncio
async def test_sdk_client_call_error():
    """SDK client should raise on sidecar error response."""
    mock_response = httpx.Response(
        404,
        json={
            "success": False,
            "error": {"code": "INVALID_OPERATION", "message": "Not found"},
            "request_id": "abc",
        },
    )

    with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_instance.aclose = AsyncMock()
        MockClient.return_value = mock_instance

        client = TikTokShopSDKClient(
            access_token="test_token",
            sdk_base_url="http://localhost:3000",
        )
        with pytest.raises(Exception, match="INVALID_OPERATION"):
            await client.call("product", "V9999", "FakeOp")
        await client.close()


@pytest.mark.asyncio
async def test_sdk_client_gateway_compatible_request():
    """SDK client.request() should work with PlatformGateway interface."""
    mock_response = httpx.Response(
        200,
        json={
            "success": True,
            "data": {"code": 0, "data": {"shops": []}},
            "request_id": "abc",
        },
    )

    with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_instance.aclose = AsyncMock()
        MockClient.return_value = mock_instance

        client = TikTokShopSDKClient(
            access_token="test_token",
            sdk_base_url="http://localhost:3000",
        )
        # Gateway-compatible interface
        result = await client.request(
            "GET", "/authorization/202309/shops",
        )
        assert "data" in result
        await client.close()


@pytest.mark.asyncio
async def test_sdk_client_passes_shop_cipher():
    """SDK client should include shop_cipher in request body."""
    mock_response = httpx.Response(
        200,
        json={"success": True, "data": {}, "request_id": "abc"},
    )

    with patch("backend.tiktok.shop.sdk_client.httpx.AsyncClient") as MockClient:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_instance.aclose = AsyncMock()
        MockClient.return_value = mock_instance

        client = TikTokShopSDKClient(
            access_token="test_token",
            shop_cipher="TTP_abc123",
            sdk_base_url="http://localhost:3000",
        )
        await client.call("product", "V202502", "ProductsSearchPost")

        call_kwargs = mock_instance.post.call_args[1]
        assert call_kwargs["json"]["shop_cipher"] == "TTP_abc123"
        await client.close()
```

**Step 2: Run tests — expect FAIL**

```bash
pytest tests/unit/tiktok/test_shop_sdk_client.py -v
```
Expected: `ModuleNotFoundError: No module named 'backend.tiktok.shop.sdk_client'`

**Step 3: Commit failing tests**

```bash
git add tests/unit/tiktok/test_shop_sdk_client.py
git commit -m "test: add failing tests for TikTokShopSDKClient"
```

---

## Task 8: Build the Python SDK Client

**Files:**
- Create: `backend/tiktok/shop/sdk_client.py`

**Step 1: Implement the SDK client**

```python
import logging
import re
from typing import Any

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

# Map REST paths to SDK domain/version/operation
# e.g. "/product/202309/products/search" → ("product", "V202309", "ProductsSearchPost")
# This allows the gateway-compatible .request()/.get()/.post() interface to work.
_PATH_TO_OPERATION: dict[str, tuple[str, str, str]] = {
    "/authorization/202309/shops": ("authorization", "V202309", "GetActiveShopsGet"),
    "/product/202309/products/search": ("product", "V202309", "ProductsSearchPost"),
    "/product/202309/products": ("product", "V202309", "ProductsPost"),
    "/product/202312/products/{product_id}/partial_edit": ("product", "V202312", "ProductsPartialEditPost"),
    "/product/202309/categories": ("product", "V202309", "CategoriesGet"),
    "/product/202309/images/upload": ("product", "V202309", "ImagesUploadPost"),
    "/order/202309/orders": ("order", "V202309", "OrdersPost"),
    "/return_refund/202309/cancellations": ("returnrefund", "V202309", "CancellationsPost"),
}


class TikTokShopSDKError(Exception):
    """Error from the TikTok Shop SDK sidecar."""

    def __init__(self, code: str, message: str, details: Any = None) -> None:
        self.code = code
        self.details = details
        super().__init__(f"{code}: {message}")


class TikTokShopSDKClient:
    """Client that proxies TikTok Shop API calls through the Node.js SDK sidecar.

    Provides two interfaces:
    1. Direct: client.call(domain, version, operation, params, body)
    2. Gateway-compatible: client.request(method, path, params, json_body)
       This allows drop-in replacement of TikTokShopClient within PlatformGateway.
    """

    def __init__(
        self,
        access_token: str,
        shop_cipher: str | None = None,
        sdk_base_url: str | None = None,
    ) -> None:
        self._access_token = access_token
        self._shop_cipher = shop_cipher
        self._base_url = sdk_base_url or settings.tiktok_shop_sdk_url
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=60.0,
        )

    async def call(
        self,
        domain: str,
        version: str,
        operation: str,
        *,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call an SDK operation directly by domain/version/operation."""
        url = f"/api/shop/{domain}/{version}/{operation}"
        payload: dict[str, Any] = {
            "access_token": self._access_token,
        }
        if self._shop_cipher:
            payload["shop_cipher"] = self._shop_cipher
        if params:
            payload["params"] = params
        if body:
            payload["body"] = body

        response = await self._client.post(url, json=payload)
        data = response.json()

        if not data.get("success"):
            error = data.get("error", {})
            raise TikTokShopSDKError(
                code=error.get("code", "UNKNOWN"),
                message=error.get("message", "Unknown error"),
                details=error.get("details"),
            )

        return data.get("data", {})

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Gateway-compatible interface matching TikTokShopClient.request().

        Translates REST path to SDK operation and delegates to call().
        """
        domain, version, operation = self._resolve_path(path)
        return await self.call(
            domain, version, operation,
            params=params,
            body=json_body,
        )

    async def get(
        self, path: str, params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return await self.request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return await self.request("POST", path, params=params, json_body=json_body)

    async def close(self) -> None:
        await self._client.aclose()

    def _resolve_path(self, path: str) -> tuple[str, str, str]:
        """Resolve a REST API path to (domain, version, operation).

        First checks the static map, then attempts regex-based resolution.
        """
        # Strip leading slash for consistency
        clean = path.lstrip("/")

        # Check static map
        for pattern, resolved in _PATH_TO_OPERATION.items():
            if clean == pattern.lstrip("/"):
                return resolved

        # Attempt dynamic resolution from path pattern:
        # /{domain}/{version}/...
        match = re.match(r"^([a-z_]+)/(\d{6})/(.+)$", clean)
        if match:
            domain = match.group(1).replace("_", "")
            version = f"V{match.group(2)}"
            # Convert rest of path to PascalCase operation name
            rest = match.group(3)
            parts = re.split(r"[/_]", rest)
            operation = "".join(p.capitalize() for p in parts if p) + "Post"
            return (domain, version, operation)

        raise TikTokShopSDKError(
            code="PATH_NOT_RESOLVED",
            message=f"Cannot resolve path '{path}' to an SDK operation",
        )
```

**Step 2: Run the tests**

```bash
pytest tests/unit/tiktok/test_shop_sdk_client.py -v
```
Expected: All 4 tests PASS.

**Step 3: Commit**

```bash
git add backend/tiktok/shop/sdk_client.py
git commit -m "feat: add TikTokShopSDKClient for sidecar communication"
```

---

## Task 9: Migrate ShopService to Use SDK Client

**Files:**
- Modify: `backend/modules/commerce/services/shop_service.py:6,100-115` — swap client import and instantiation

**Step 1: Update imports**

Replace:
```python
from backend.tiktok.shop.client import TikTokShopClient
```
With:
```python
from backend.tiktok.shop.sdk_client import TikTokShopSDKClient
```

**Step 2: Update _build_gateway()**

Replace `TikTokShopClient` instantiation in `_build_gateway()` (line ~110):
```python
        client = TikTokShopClient(access_token=access_token)
```
With:
```python
        client = TikTokShopSDKClient(access_token=access_token)
```

**Step 3: Update build_gateway_for_shop()**

Replace `TikTokShopClient` instantiation in `build_gateway_for_shop()` (line ~140):
```python
        client = TikTokShopClient(
            access_token=access_token,
            shop_cipher=shop.shop_cipher,
        )
```
With:
```python
        client = TikTokShopSDKClient(
            access_token=access_token,
            shop_cipher=shop.shop_cipher,
        )
```

**Step 4: Update PlatformClient type alias in gateway.py**

In `backend/tiktok/gateway.py`, add the SDK client to the union type:
```python
from backend.tiktok.shop.sdk_client import TikTokShopSDKClient
```
And update:
```python
PlatformClient = (
    TikTokShopClient
    | TikTokShopSDKClient
    | TikTokDeveloperClient
    | TikTokMarketingClient
    | TikTokResearchClient
    | TikTokLiveClientWrapper
)
```

**Step 5: Run existing tests**

```bash
pytest tests/unit/commerce/ -v
pytest tests/unit/tiktok/ -v
```
Expected: All tests PASS (existing tests mock the client, so they should work).

**Step 6: Commit**

```bash
git add backend/modules/commerce/services/shop_service.py backend/tiktok/gateway.py
git commit -m "feat: migrate ShopService to TikTokShopSDKClient"
```

---

## Task 10: Docker Compose Smoke Test

**Step 1: Build and start the full stack**

```bash
docker compose up --build -d
```

**Step 2: Verify sidecar health**

```bash
curl http://localhost:3000/health
```
Expected: `{"status":"ok"}`

Note: Port 3000 may not be exposed externally. Test from inside Docker:
```bash
docker compose exec api curl http://tiktok-shop-sdk:3000/health
```
Expected: `{"status":"ok"}`

**Step 3: Test discovery endpoint**

```bash
docker compose exec api curl http://tiktok-shop-sdk:3000/api/shop/operations | python -m json.tool | head -30
```
Expected: JSON list of all domains/versions/operations.

**Step 4: Test a live API call (product search)**

You'll need a valid access_token from your connected seller account. Run from inside the api container:

```bash
docker compose exec api curl -X POST http://tiktok-shop-sdk:3000/api/shop/product/V202309/ProductsSearchPost \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "YOUR_ACCESS_TOKEN",
    "shop_cipher": "YOUR_SHOP_CIPHER",
    "params": {"pageSize": 5},
    "body": {}
  }'
```
Expected: JSON response with `"success": true` and product data.

**Step 5: Commit any fixes**

```bash
git add -A
git commit -m "fix: docker compose smoke test adjustments"
```

---

## Task 11: Run Full Test Suite

**Step 1: Run all tests**

```bash
pytest tests/ -v --tb=short
```
Expected: 878+ tests PASS. No regressions.

**Step 2: Final commit if needed**

```bash
git add -A
git commit -m "test: verify full test suite passes with SDK sidecar integration"
```

---

## Summary of Commits

| # | Message | What |
|---|---------|------|
| 1 | `chore: scaffold tiktok-shop-sdk sidecar with official SDK` | Project structure + SDK copy |
| 2 | `feat(sdk-sidecar): add SDK registry for dynamic operation resolution` | Registry maps domain+version → API class |
| 3 | `feat(sdk-sidecar): add Fastify server with dynamic operation router` | Server + generic proxy route |
| 4 | `chore(sdk-sidecar): add Dockerfile for Node.js sidecar` | Docker build |
| 5 | `feat: add tiktok-shop-sdk sidecar to Docker Compose` | Docker Compose integration |
| 6 | `feat: add tiktok_shop_sdk_url to settings` | Python config |
| 7 | `test: add failing tests for TikTokShopSDKClient` | TDD red phase |
| 8 | `feat: add TikTokShopSDKClient for sidecar communication` | TDD green phase |
| 9 | `feat: migrate ShopService to TikTokShopSDKClient` | First service migration |
| 10 | `fix: docker compose smoke test adjustments` | Live validation |
| 11 | `test: verify full test suite passes with SDK sidecar integration` | Regression check |
