# Contributing to Frodo

> Unified TikTok SaaS Platform - "One platform to rule them all"

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Backend runtime |
| Node.js | 20+ | Frontend runtime |
| Docker & Docker Compose | Latest | Local services (PostgreSQL, Redis) |
| Git | Latest | Version control |

## Environment Setup

### 1. Clone and install backend

```bash
git clone <repo-url> && cd frodo
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Install frontend

```bash
cd frontend
npm install
cd ..
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your values (see Environment Variables below)
```

### 4. Start infrastructure

```bash
docker compose up -d postgres redis
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start development servers

```bash
# Terminal 1: Backend API
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Celery worker
celery -A backend.workers.celery_app worker --loglevel=info --concurrency=4

# Terminal 3: Celery beat (scheduler)
celery -A backend.workers.celery_app beat --loglevel=info

# Terminal 4: Frontend
cd frontend && npm run dev
```

Or start everything via Docker Compose:

```bash
docker compose up
```

## Environment Variables

> Source of truth: `.env.example`

| Variable | Purpose | Format | Required |
|----------|---------|--------|----------|
| `APP_NAME` | Application name | String | Yes |
| `APP_ENV` | Environment (`development`, `staging`, `production`) | String | Yes |
| `DEBUG` | Enable debug mode | `true`/`false` | Yes |
| `SECRET_KEY` | App-level secret key | Random string | Yes |
| `FRONTEND_URL` | Frontend origin for CORS | URL | Yes |
| `BACKEND_URL` | Backend base URL | URL | Yes |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:port/db` | Yes |
| `REDIS_URL` | Redis connection string | `redis://host:port/db` | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | Random string | Yes |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | Integer (default: 15) | Yes |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | Integer (default: 7) | Yes |
| `TOKEN_VAULT_KEY` | AES-256 encryption key for token vault | Base64-encoded 32-byte key | Yes |
| `TIKTOK_SHOP_APP_KEY` | TikTok Shop app key | String | For Shop features |
| `TIKTOK_SHOP_APP_SECRET` | TikTok Shop app secret | String | For Shop features |
| `TIKTOK_DEVELOPER_CLIENT_KEY` | TikTok Developer client key | String | For Developer features |
| `TIKTOK_DEVELOPER_CLIENT_SECRET` | TikTok Developer client secret | String | For Developer features |
| `TIKTOK_MARKETING_APP_ID` | TikTok Marketing app ID | String | For Ads features |
| `TIKTOK_MARKETING_APP_SECRET` | TikTok Marketing app secret | String | For Ads features |
| `CELERY_BROKER_URL` | Celery broker (Redis) | `redis://host:port/db` | Yes |
| `CELERY_RESULT_BACKEND` | Celery result store (Redis) | `redis://host:port/db` | Yes |

## Available Scripts

### Backend (Python)

| Command | Description |
|---------|-------------|
| `uvicorn backend.main:app --reload` | Start FastAPI dev server (port 8000) |
| `celery -A backend.workers.celery_app worker --loglevel=info` | Start Celery worker |
| `celery -A backend.workers.celery_app beat --loglevel=info` | Start Celery beat scheduler |
| `alembic upgrade head` | Run database migrations |
| `alembic revision --autogenerate -m "description"` | Generate new migration |
| `alembic downgrade -1` | Rollback last migration |
| `pytest` | Run all tests |
| `pytest tests/unit` | Run unit tests only |
| `pytest tests/integration` | Run integration tests only |
| `pytest --cov=backend --cov-report=term-missing` | Run tests with coverage |
| `black backend/ tests/` | Format code |
| `isort backend/ tests/` | Sort imports |
| `ruff check backend/ tests/` | Lint code |
| `ruff check --fix backend/ tests/` | Auto-fix lint issues |
| `mypy backend/` | Type checking |
| `bandit -r backend/` | Security scanning |

### Frontend (Node.js / Next.js)

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Next.js dev server (port 3000) |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | ESLint check |

### Docker Compose

| Command | Description |
|---------|-------------|
| `docker compose up` | Start all services (api, celery, postgres, redis) |
| `docker compose up -d postgres redis` | Start infrastructure only |
| `docker compose down` | Stop all services |
| `docker compose down -v` | Stop and remove volumes (destroys data) |
| `docker compose logs -f api` | Follow API logs |
| `docker compose logs -f celery-worker` | Follow Celery worker logs |

## Docker Services

| Service | Image / Build | Port | Healthcheck |
|---------|--------------|------|-------------|
| `api` | Custom (Dockerfile) | 8000 | `curl -f http://localhost:8000/health` |
| `celery-worker` | Custom (Dockerfile) | - | - |
| `celery-beat` | Custom (Dockerfile) | - | - |
| `postgres` | `postgres:16-alpine` | 5432 | `pg_isready -U frodo` |
| `redis` | `redis:7-alpine` | 6379 | `redis-cli ping` |

## Project Structure

```
frodo/
  backend/
    main.py                 # FastAPI app factory
    config.py               # pydantic-settings
    dependencies.py         # DI (DB sessions, current user)
    auth/                   # JWT, RBAC, passwords, routes
    db/                     # SQLAlchemy engine, models, migrations
    tiktok/                 # Platform clients (shop/developer/marketing)
    modules/                # Business domains (connect, commerce, ads, content, creators, analytics, webhooks)
    workers/                # Celery tasks (token refresh, webhook processing, data sync)
    middleware/             # Tenant, logging middleware
    utils/                  # Crypto, pagination
  frontend/
    src/app/(auth)/         # Login, register pages
    src/app/(dashboard)/    # Dashboard pages with sidebar layout
  tests/
    unit/                   # Unit tests (37+ passing)
    integration/            # Integration tests
    e2e/                    # End-to-end tests (placeholder)
  knowledge-base/           # TikTok API research (60 markdown files)
  docs/                     # Project documentation
```

## Testing

### Running tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# With coverage report
pytest --cov=backend --cov-report=term-missing

# Specific test file
pytest tests/unit/test_jwt.py -v
```

### Test markers

```bash
pytest -m unit       # Unit tests
pytest -m integration  # Integration tests
pytest -m e2e        # E2E tests
```

### Current test coverage

- JWT token creation/validation
- AES-256-GCM encryption/decryption
- Password hashing (bcrypt)
- RBAC role/permission checks
- Circuit breaker state transitions
- Webhook signature verification (all 3 platforms)
- HMAC-SHA256 request signing (Shop API)
- Pagination utilities
- Commerce schemas, webhook handlers, services

## Code Quality

### Formatting & linting

```bash
black backend/ tests/        # Format
isort backend/ tests/        # Sort imports
ruff check backend/ tests/   # Lint
ruff check --fix backend/    # Auto-fix
```

### Configuration (pyproject.toml)

| Tool | Config |
|------|--------|
| black | line-length=88, target py312 |
| isort | profile=black, line-length=88 |
| ruff | E, F, W, I, N, UP, S, B, A, C4, SIM rules |
| mypy | strict mode, pydantic plugin |
| pytest | asyncio_mode=auto, testpaths=tests |

## Development Workflow

1. Create a feature branch from `main`
2. Write tests first (TDD approach)
3. Implement the feature
4. Run `black`, `isort`, `ruff check`, `mypy`
5. Run `pytest --cov=backend`
6. Commit with conventional commit format: `feat:`, `fix:`, `refactor:`, etc.
7. Open a pull request

## API Documentation

When running in debug mode (`DEBUG=true`), interactive API docs are available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

### API Route Prefixes

| Prefix | Module | Description |
|--------|--------|-------------|
| `/api/auth` | auth | Login, register, token refresh |
| `/api/connect` | connect | TikTok OAuth flows, account management |
| `/api/commerce` | commerce | Shop, products, orders, fulfillment, returns |
| `/api/ads` | advertising | Ad accounts, campaigns, reporting |
| `/api/content` | content | Video management, content posting |
| `/api/creators` | creators | Creator discovery, partnerships |
| `/api/analytics` | analytics | Cross-platform dashboards |
| `/webhooks` | webhooks | TikTok webhook ingestion (no `/api` prefix) |
