# Frodo — Engineering Team Meeting: Talking Points

> Handover meeting guide for engineers taking Frodo to production.

---

## 1. Opening / Elevator Pitch

Frodo is a unified SaaS dashboard for agencies managing brands on TikTok. TikTok's ecosystem is split across four completely separate platforms — Shop, Developer, Marketing, and LIVE — each with its own authentication, signing mechanisms, rate limits, and webhooks. Frodo builds the unification layer TikTok doesn't provide: connect all your accounts once, manage everything from one place.

---

## 2. Platform Overview

What Frodo does today:

- **Account Connection** — OAuth flows for Shop (HMAC), Developer (Bearer), and Marketing (custom header) platforms
- **Commerce** — Product catalog sync, order management, fulfillment, returns, affiliate management
- **Advertising** — Campaign/ad group/ad hierarchy, metrics, async reporting, Business Center
- **Content** — Video library with metrics, content publishing, content calendar
- **Creator Marketplace** — Creator discovery, profiles, Spark Ads workflow
- **Analytics** — Cross-platform unified KPIs, export (CSV/Excel)
- **Real-Time** — WebSocket updates for commerce events and sync progress (Redis pub/sub)
- **Background Automation** — 20 Celery beat schedules: token refresh, data sync, reports

---

## 3. Tech Stack Summary

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | Python 3.12 + FastAPI | Async-native, type hints, auto OpenAPI generation |
| Database | PostgreSQL 16 | Multi-tenant via Row-Level Security, JSONB for flexible platform data |
| Cache / Broker | Redis 7 | Token cache, Celery broker, rate-limit counters, pub/sub |
| Task Queue | Celery 5 + Beat | Token refresh, data sync, report generation, 20 periodic tasks |
| Frontend | Next.js 15 (App Router) + React 19 | Server components, middleware auth, TypeScript throughout |
| SDK Sidecar | Node.js 20 + Fastify | TikTok Shop HMAC signing proxy (Node has better HMAC-SHA256 support) |
| Object Storage | S3 / Cloudflare R2 | Media assets, async report exports |
| Secrets | AWS Secrets Manager / Vault | Encrypted token vault keys (not in env vars) |
| Deploy | Docker Compose → Kubernetes | 6 services today; horizontal scaling path already defined |

---

## 4. Key Architectural Decisions

### 4.1 Multi-Tenancy: Shared DB + workspace_id
- Model: `Organization > Workspace > Membership`
- All tenant-scoped tables carry a `workspace_id` FK
- PostgreSQL Row-Level Security enforces isolation at the DB layer
- Roles: `owner > admin > manager > member > viewer`
- **Why not separate schemas/DBs?** Operational simplicity at this scale; RLS is the guard

### 4.2 Token Security: AES-256-GCM Vault
- All TikTok tokens stored encrypted in `token_vault` table
- Vault key lives in Secrets Manager, not in `.env`
- **Critical**: Rotating `TOKEN_VAULT_KEY` requires a migration script to re-encrypt all rows — do not rotate casually

### 4.3 API Gateway Pattern
- `backend/tiktok/gateway.py` is the single facade for all 4 TikTok platforms
- Every outbound call passes through: **Rate Limiter → Circuit Breaker → Retry**
  - Rate Limiter: Redis token bucket (Shop=50 QPS, Developer=600/min)
  - Circuit Breaker: open after 5 failures in 60s, per-platform isolation
  - Retry: exponential backoff (1s→2s→4s), max 3x, only on 429/5xx
- **Three different signing mechanisms** (see 4.4) are abstracted behind the gateway

### 4.4 Three TikTok Signing Mechanisms
Each platform has a completely different auth scheme:

| Platform | Signing | Header |
|----------|---------|--------|
| Shop | HMAC-SHA256 (query signing + body) | `x-tts-access-token` |
| Developer | Standard Bearer token | `Authorization: Bearer` |
| Marketing | Custom header | `Access-Token: {token}` |

The SDK Sidecar (Node.js) handles HMAC signing for Shop API because of better native support — the Python backend proxies Shop requests through it.

### 4.5 Webhook + Polling Dual Strategy
- Webhooks are the primary update path (3 endpoints with platform-specific signature verification)
- Celery periodic tasks poll as a fallback/reconciliation layer (every 5-15 min for orders)
- This is intentional: TikTok webhook delivery is not guaranteed
- All webhooks stored immutably in `webhook_events` with idempotency keys (Redis SETNX)

### 4.6 Domain Module Pattern
Every business domain follows the same structure:
```
modules/<domain>/
├── routes/          # FastAPI routers
├── services/        # Business logic
├── schemas.py       # Pydantic request/response models
└── webhook_handlers.py  (if applicable)
```
This makes onboarding predictable — find the domain, find the same files.

### 4.7 Celery Beat: Single Instance Constraint
- Celery Beat scheduler **must run as a single instance** — duplicate schedulers create duplicate tasks
- In Kubernetes: use a `Deployment` with `replicas: 1` (not a DaemonSet)
- Workers can scale horizontally; Beat cannot

---

## 5. Current State

| Dimension | Status |
|-----------|--------|
| Version | 0.1.0 — pre-production |
| Tests | 879 total: 842 unit + 37 integration |
| Backend modules | 11 domain modules (connect, commerce, advertising, content, creators, analytics, webhooks, intelligence, live, messaging, notifications) |
| Data models | 18 ORM model files |
| TikTok clients | 4 platform clients (shop, developer, marketing, live/research) |
| Frontend | 13 dashboard sections, 1500-line typed API client |
| Migrations | Alembic-managed (social_identities + nullable password migration applied) |
| CI/CD | Not yet configured |
| Production infra | Not yet provisioned |
| Phase 7 (Intelligence) | In progress — SDK sidecar integration tests pending |

**What works today:** Full local development stack via Docker Compose. Auth, multi-tenancy, token vault, and the gateway pattern are solid. Unit test coverage is the strongest signal of code correctness right now.

---

## 6. What's Needed for Production

### Immediate (before first deploy)
- [ ] Provision production PostgreSQL with RLS enabled and connection pooling (PgBouncer recommended)
- [ ] Provision production Redis (cluster mode or at minimum persistence enabled)
- [ ] Set up Secrets Manager / Vault and move `TOKEN_VAULT_KEY`, `JWT_SECRET_KEY`, `SECRET_KEY` out of `.env`
- [ ] Configure all TikTok app credentials (one set per platform: shop, developer, marketing)
- [ ] Set `DEBUG=false` — this disables API docs and tightens CORS
- [ ] Container registry + CI/CD pipeline (build → test → push → deploy)
- [ ] Celery Beat deployed as single-replica deployment

### Short-term (first sprint)
- [ ] Observability: structured logging aggregation (Datadog, Grafana Loki, etc.)
- [ ] APM: p95 API latency, error rate tracking
- [ ] Alerts on: token refresh failures, webhook processing lag, queue depth > 1000
- [ ] E2E tests (Playwright) — register → connect Shop → view products → fulfill order
- [ ] S3/R2 bucket provisioned for async report exports
- [ ] TikTok app credentials verified against production TikTok developer portals

### Medium-term
- [ ] Kubernetes manifests (API horizontal, Beat single-replica, Worker horizontal)
- [ ] Read replicas for PostgreSQL as query load grows
- [ ] SDK sidecar integration tests completed
- [ ] Security scan baseline (Bandit + `pip audit`) in CI
- [ ] Phase 7 Intelligence platform completion

### Known gaps
- **LIVE platform** — deferred; requires TikTok partner-level API access
- **Billing** — Stripe integration is planned but not built
- **Email notifications** — not yet wired up
- **Load testing** — rate limiter behavior under concurrent requests untested at scale

---

## 7. Suggested Meeting Flow

| # | Topic | Time | Lead |
|---|-------|------|------|
| 1 | Elevator pitch + problem statement | 5 min | Product |
| 2 | Platform overview (what it does) | 10 min | Product/Eng |
| 3 | Tech stack walkthrough | 10 min | Eng |
| 4 | Key architectural decisions (4.1–4.7) | 20 min | Eng |
| 5 | Live code tour: gateway + one module | 15 min | Eng |
| 6 | Current state + test coverage | 5 min | Eng |
| 7 | Production readiness gaps | 15 min | All |
| 8 | Open questions (see Section 8) | 15 min | All |
| 9 | Ownership assignments + next steps | 5 min | Lead |

**Total: ~100 minutes.** Run sections 3–5 with the codebase open.

---

## 8. Key Questions to Discuss

### Infrastructure & Ops
1. **Kubernetes vs. ECS?** The RUNBOOK assumes Kubernetes. If ECS, Celery Beat single-instance constraint needs special handling.
2. **Which cloud?** AWS (Secrets Manager native), GCP, or self-hosted? Affects secrets management integration.
3. **Connection pooling strategy?** PgBouncer as sidecar or managed (RDS Proxy)? Async SQLAlchemy needs transaction mode pooling.

### Security
4. **TOKEN_VAULT_KEY rotation policy?** This key encrypts all TikTok tokens. Rotation requires a migration script. What's the cadence and who owns it?
5. **Webhook IP allowlisting?** TikTok publishes IP ranges for webhook delivery — should we enforce at the load balancer level?

### Architecture
6. **SDK Sidecar deployment model?** The Node.js HMAC sidecar must be co-located or accessible from the API. Sidecar container in the same pod, or separate service?
7. **Cross-platform identity linking** — currently manual in the UI. Is automatic linking (by TikTok user ID) a near-term requirement?

### Reliability
8. **Dead letter queue for failed Celery tasks?** Currently errors are logged and retried. Do we need a DLQ with alerting for persistent failures?
9. **Webhook replay capability?** The `webhook_events` table stores raw payloads — do we want a `/webhooks/replay/{id}` endpoint for operations?

### Product
10. **Which TikTok developer app credentials does the team have?** All three platforms (Shop, Developer, Marketing) require separate app registrations with TikTok. These must be confirmed before any production traffic.

---

## 9. Resource Index

| Document | What's Inside | Path |
|----------|--------------|------|
| CLAUDE.md | Project quick-start, stack, commands, patterns | `/CLAUDE.md` |
| ARCHITECTURE.md | Full system design, DDL schema, phasing plan, risk register | `/ARCHITECTURE.md` |
| CONTRIB.md | Local setup guide, env vars, dev scripts | `/docs/CONTRIB.md` |
| RUNBOOK.md | Ops procedures, monitoring metrics, common fixes, rollback | `/docs/RUNBOOK.md` |
| CODEMAPS/ | Auto-generated architecture maps (4 files: arch, backend, frontend, data) | `/docs/CODEMAPS/` |
| plans/ | 19 implementation plan files (per-phase, per-feature) | `/docs/plans/` |
| knowledge-base/ | 60-file TikTok API research library (endpoints, limits, gotchas) | `/knowledge-base/` |
| api-integration-manual.md | TikTok API integration details per platform | `/docs/api-integration-manual.md` |

---

*Document created: 2026-03-04 | Version: 0.1.0 | Status: Pre-production handover*
