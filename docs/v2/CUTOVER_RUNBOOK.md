# Frodo Python → v2 cutover runbook (Phase 9)

Use this when Node services are ready to own traffic and background work.

## Supabase as managed PostgreSQL

Use Supabase **only** as hosted Postgres unless/until the stack explicitly adopts its other products.

- **Do not** route Frodo v2 authentication through Supabase Auth; keep **`JWT_SECRET`** and existing API auth.
- **Do not** depend on Supabase Realtime or Storage for Shop vertical slices yet.
- Create a Supabase project → **Settings → Database** → copy connection strings.
  - **`DATABASE_URL` (API/worker on Railway):** typically the **transaction pooler** URI (e.g. port **6543**) when Supabase recommends it for application servers.
  - **`DATABASE_MIGRATION_URL` (optional):** use the **direct** URI (e.g. **`db.<project-ref>.supabase.co:5432`**) for **`pnpm db:migrate`** and Drizzle Kit if the pooler is unsuitable for DDL. If unset, migrations use **`DATABASE_URL`**.
- On **Railway**, set **`DATABASE_URL`** on the API and worker services; set **`DATABASE_MIGRATION_URL`** only when you split pooler vs direct (variables UI, same as other secrets).

Full detail: **`docs/v2/ENVIRONMENT.md`** (PostgreSQL URLs).

Railway multi-service layout, build/start commands, and IAM: **`docs/v2/RAILWAY_DEPLOYMENT.md`**.

## Staging validation sequence (Shop Connect + commerce)

Run in order before signing off staging:

1. `pnpm db:check` — confirms connectivity and core tables (no secrets printed).
2. `pnpm db:migrate` — applies Drizzle migrations (**requires** `DATABASE_MIGRATION_URL` or `DATABASE_URL`).
3. `pnpm build`
4. `pnpm test`
5. `pnpm lint`
6. Start **API**, **worker**, and **web** with production-like env (see **`docs/v2/ENVIRONMENT.md`**).
7. Complete **Shop Connect** OAuth once for the workspace under test.
8. `pnpm validate:shop-connect -- --workspace "<workspace-uuid>"` (with `DATABASE_URL` set, or `DATABASE_MIGRATION_URL` if `DATABASE_URL` is unset).
9. Trigger **product** and **order** sync (UI or commerce POST endpoints).
10. `pnpm validate:shop-commerce -- --workspace "<workspace-uuid>" --shop "<shops.id uuid>"`.

TikTok-specific checklist and failure modes: **`docs/v2/TIKTOK_SHOP_STAGING_VALIDATION.md`**.

## Preconditions

- Staging parity checks passed for auth, webhooks, commerce sync (sample workspaces).
- `scheduled_job_runs` and `feature_flags` migrations applied.
- SQS + DLQ configured; worker health verified (messages consumed, DLQ empty under steady state).
- TikTok developer apps: callback URLs point to v2 API hosts.

## Steps

1. **Freeze Python writes**: Stop Celery workers and Celery Beat (`docker compose stop` or equivalent); keep FastAPI read-only if needed for rollback comparison.
2. **Route traffic**: Point DNS / edge router to `apps/api` and static SPA (`apps/web` build). Keep FastAPI on internal URL for debugging until retired.
3. **Verify jobs**: Confirm scheduler cron POSTs `internal/cron/tick`; worker logs show `token_refresh_tick` and domain jobs without DLQ growth.
4. **Webhooks**: Point TikTok webhook URLs to v2 ingress (`/api/webhooks/shop`). Monitor `webhook_events` status distribution.
5. **Rollback**: If critical failure, restore Celery + Beat and DNS to FastAPI; DB migrations from v2 are additive—no schema rollback required for `scheduled_job_runs` / `feature_flags`.

## Post-cutover

- Archive Python deployment manifests; keep `backend/` in repo until parity sign-off.
- Replace mock-heavy TikTok tests with recorded HTTP fixtures against sandbox apps.

---

## TikTok Shop OAuth — local / staging (v2)

Full staging checklist (Partner settings, env vars, logs, DB verification, failure modes): **`docs/v2/TIKTOK_SHOP_STAGING_VALIDATION.md`**.

1. **Partner Center**: Register redirect URI exactly as `TIKTOK_SHOP_REDIRECT_URI`. Nest serves callbacks under the global prefix **`/api`**, e.g. `http://localhost:8001/api/connect/shop/callback`.
2. **API `.env`**: Set `TIKTOK_SHOP_APP_KEY`, `TIKTOK_SHOP_APP_SECRET`, `TIKTOK_SHOP_SERVICE_ID`, `TIKTOK_SHOP_REDIRECT_URI`, `TOKEN_ENCRYPTION_KEY`, `PUBLIC_WEB_ORIGIN=http://localhost:5173`, plus DB/Redis/JWT/SQS (use real SQS for end-to-end discovery; `ALLOW_ASYNC_SKIP=true` is dev-only and still fails enqueue closed — Shop connect rolls back if enqueue fails).
3. **Worker `.env`**: Same DB/SQS as API; add `TOKEN_ENCRYPTION_KEY`, `TIKTOK_SHOP_APP_KEY`, `TIKTOK_SHOP_APP_SECRET` so `shop_discovery_after_connect` can call `GET /authorization/202309/shops`.
4. **Run**: `pnpm dev:api`, `pnpm dev:worker`, `pnpm dev:web` → register/login → **Workspace** → **Connect Shop** → complete TikTok consent → browser lands on `/connect/shop/result` → **Shops** shows DB + recent `sync_jobs`.
5. **Failure cues**: `tiktok_token_missing_seller_identity` means token JSON lacked `open_id` / `seller_id` — capture raw response (tokens are never logged) and adjust parser in `@frodo/domain` `token-exchange.ts`.
