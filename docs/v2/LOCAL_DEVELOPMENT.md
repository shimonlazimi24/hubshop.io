# Frodo v2 — local development (Node monorepo)

The root **`docker-compose.yml`** targets the **legacy Python** stack (`uvicorn`, Celery). For **`apps/api`**, **`apps/worker`**, and **`apps/web`**, run the Node toolchain directly.

The **`apps/web`** SPA uses **Tailwind CSS v3**, **lucide-react** icons, and small reusable UI components under `src/components/ui/` — no heavy UI framework.

## Preview the web UI only (no database, no API)

The SPA can run alone to click through routes and see layout. API calls (login, shops, etc.) will fail until the API is up.

From repo root **without global `pnpm`**:

```bash
npx --yes pnpm@9.15.4 install
npm run dev
```

**Do not run `npm install` at the monorepo root** — this repo uses **`pnpm-lock.yaml`**, not npm’s lockfile. npm can crash with errors like `Cannot read properties of null (reading 'matches')` or produce a broken tree.

This runs `vite` for `apps/web` (via `npx pnpm@9.15.4 dev:web`). Open the URL Vite prints (usually `http://localhost:5173`).

**There is no “full Frodo backend” mode without Postgres:** the API validates `DATABASE_URL` at startup and uses Drizzle/Postgres for real data. The smallest “real” setup is a local Postgres (e.g. one Docker container) plus `apps/api/.env` — see below.

### Why `npm run dev` used to do nothing useful

The monorepo is driven by **pnpm workspaces**. Historically the root `package.json` had **`dev:api`** / **`dev:web`** but **no** script named **`dev`**, so `npm run dev` failed with **missing script** or users expected one command for everything. Root **`dev`** is now wired to **web-only**; full stack still needs **two terminals**: API + web.

## Prerequisites

- **Node.js ≥ 20** (tested with current LTS; Node 22+ enforces `package.json` `exports` correctly — workspace packages must expose `require` for Nest).
- **pnpm** — from repo root: `corepack enable` / `npm i -g pnpm`, or `npx pnpm@9.15.4 …`.
- **PostgreSQL** reachable from your machine (local Docker, Supabase, etc.) — **only if you run the API**.
- Optional: **Redis** (recommended if you test logout/blacklist); for minimal UI/API smoke tests you can omit it when **`APP_ENV=development`** (see below).

## 1. Install and build workspace packages

From the **repository root**:

```bash
pnpm install --frozen-lockfile
pnpm --filter @frodo/contracts build && pnpm --filter @frodo/config build && pnpm --filter @frodo/db build && pnpm --filter @frodo/domain build
```

(`pnpm build` at root builds everything including API/worker/web.)

## 2. Database

Use a **`postgresql://`** or **`postgres://`** URI for **`DATABASE_URL`**.  
**Do not** use `postgresql+asyncpg://` (that is for Python); Node’s `postgres` driver will not accept it.

Examples:

- Local: `postgresql://frodo:frodo@127.0.0.1:5432/frodo`
- Supabase: copy URI from the dashboard (often append `?sslmode=require`).

Apply migrations:

```bash
export DATABASE_URL='postgresql://…'
pnpm --filter @frodo/db build
pnpm db:migrate
pnpm db:check
```

## 3. API environment

Nest loads **`.env`** from **`apps/api`** (working directory of `pnpm --filter @frodo/api …`).

Copy the template:

```bash
cp apps/api/.env.example apps/api/.env
# edit DATABASE_URL, JWT_SECRET, etc.
```

Minimal **development** flags:

- **`APP_ENV=development`**
- **`ALLOW_ASYNC_SKIP=true`** — allows API startup **without** SQS (Shop Connect enqueue will still fail closed unless you configure AWS or use mocks).

Set **`PUBLIC_WEB_ORIGIN=http://localhost:5173`** so CORS matches the Vite dev server.

## 4. Run services

From **repo root**:

```bash
pnpm dev:api    # Nest watch — http://localhost:8001 (or PORT)
pnpm dev:web    # Vite — http://localhost:5173
```

Worker (needs real SQS unless you only develop API-only flows):

```bash
pnpm dev:worker
```

For worker locally without AWS, you still need **`AWS_REGION`**, **`SQS_QUEUE_URL`**, and IAM vars — there is no async skip on the worker.

## 5. Common failures

| Symptom | Likely cause |
|---------|----------------|
| `ERR_PACKAGE_PATH_NOT_EXPORTED` / `@frodo/domain` | Fixed in repo: `exports.require` on workspace packages; run `pnpm install` and rebuild packages. |
| `DATABASE_URL is required` / invalid env | Missing **`apps/api/.env`** or wrong variable names. |
| Postgres connection errors | Wrong URL, DB down, or **`+asyncpg`** in URL. |
| `ALLOW_ASYNC_SKIP is only permitted when APP_ENV=development` | Set **`APP_ENV=development`** if using async skip. |
| Shop connect rolls back / 503 on enqueue | SQS not configured — expected without AWS; configure **`AWS_REGION`** + **`SQS_QUEUE_URL`** or test non-shop flows first. |
| CORS errors from browser | **`PUBLIC_WEB_ORIGIN`** must exactly match the web origin (scheme + host + port). |

## 6. Health check

With API running:

```bash
curl -s http://localhost:8001/api/health
```

Expect JSON with `"ok":true`.
