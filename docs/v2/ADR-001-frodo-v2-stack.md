# ADR-001: Frodo v2 Application Stack

## Status

Accepted

## Context

Frodo is migrating from Python (FastAPI + Celery + Redis broker) + Next.js to a unified TypeScript platform with managed asynchronous work and simpler operations for a small team.

## Decision

| Concern | Choice |
|---------|--------|
| API framework | **NestJS** — modular boundaries, guards, DI, predictable testing for a large domain surface |
| Worker runtime | **Node** with shared `@frodo/domain` — same types and TikTok clients as API |
| ORM / migrations | **Drizzle ORM** + **drizzle-kit** — explicit SQL, JSONB, Postgres-first |
| Frontend | **Vite** + **React** + **React Router** — SPA fits dashboard UX; API remains separate |
| Async jobs | **AWS SQS** (Standard + DLQ) — durable, managed; workers poll from Railway (or any host) |
| Scheduling | **Railway Cron** (or external cron) → enqueue-only HTTP → SQS — no inline heavy work |
| Redis | **Optional** — rate limits, realtime pub/sub, short-lived cache; not the job broker |
| TikTok Shop signing | **In-process** in `@frodo/domain` — remove separate Fastify sidecar for v2 |

## Consequences

### Positive

- Single language and shared packages reduce duplication and drift.
- SQS provides at-least-once delivery, DLQ, and redrive without operating Redis as a queue.
- Drizzle migrations live beside TypeScript; tenant queries stay explicit.

### Negative / trade-offs

- AWS account required for SQS (IAM keys or OIDC); operational surface is small but non-zero.
- Local dev needs LocalStack or a dev AWS queue (documented in `docs/v2/.env.example` patterns).
- Full parity with Python is phased; strangler migration avoids big-bang risk.

## Alternatives considered

- **Fastify**: Faster HTTP layer but weaker convention for large modular APIs; team would rebuild Nest-like patterns.
- **Prisma**: Strong DX; heavier runtime and more escape hatches for JSONB multi-tenant queries.
- **BullMQ / Redis queue**: Conflicts with “no BullMQ” and operational preference for managed queues.
- **Cloudflare Queues**: Strong when Workers own consumption; awkward for Railway-hosted long-polling Node workers.
- **Next.js**: Dropped for v2 web app; marketing site can remain separate if SEO is needed later.

## References

- Plan: Frodo v2 Node migration (internal)
- Legacy: [CLAUDE.md](../../CLAUDE.md), [ARCHITECTURE.md](../../ARCHITECTURE.md)
