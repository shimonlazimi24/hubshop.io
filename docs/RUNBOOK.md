# Frodo Runbook

> Operational procedures for the Frodo Unified TikTok Platform

## Deployment

### Docker Compose (Development / Staging)

```bash
# Build and start all services
docker compose up --build -d

# Verify all services are healthy
docker compose ps

# Run migrations inside the container
docker compose exec api alembic upgrade head
```

### Production Deployment

1. Build the Docker image:
   ```bash
   docker build -t frodo-api:$(git rev-parse --short HEAD) .
   ```

2. Push to container registry:
   ```bash
   docker tag frodo-api:<sha> <registry>/frodo-api:<sha>
   docker push <registry>/frodo-api:<sha>
   ```

3. Run database migrations (before deploying new API):
   ```bash
   docker run --rm --env-file .env frodo-api:<sha> alembic upgrade head
   ```

4. Deploy new image to Kubernetes / ECS / target platform.

5. Verify health:
   ```bash
   curl https://<api-host>/health
   # Expected: {"status": "healthy", "version": "0.1.0"}
   ```

### Environment Checklist

Before deploying to production, verify:

- [ ] `DEBUG=false`
- [ ] `SECRET_KEY` is a strong random value (not the default)
- [ ] `JWT_SECRET_KEY` is a strong random value (not the default)
- [ ] `TOKEN_VAULT_KEY` is a proper base64-encoded 32-byte key
- [ ] `DATABASE_URL` points to production PostgreSQL
- [ ] `REDIS_URL` points to production Redis
- [ ] `FRONTEND_URL` matches the production frontend origin
- [ ] TikTok app credentials are set for all required platforms
- [ ] Celery broker/result backend URLs point to production Redis
- [ ] API docs are disabled (auto-disabled when `DEBUG=false`)

---

## Service Architecture

```
             +---------+    +---------+    +---------+
External --> |  API    |    | Celery  |    | Celery  |
Requests     | (8000)  |    | Worker  |    | Beat    |
             +----+----+    +----+----+    +----+----+
                  |              |              |
             +----v----+    +---v----+         |
             |PostgreSQL|   | Redis  |<--------+
             | (5432)   |   | (6379) |
             +----------+   +--------+
```

| Service | Scaling | Notes |
|---------|---------|-------|
| API | Horizontal (multiple replicas) | Stateless, behind load balancer |
| Celery Worker | Horizontal (multiple workers) | `--concurrency=4` per worker |
| Celery Beat | **Single instance only** | Duplicate schedulers cause duplicate tasks |
| PostgreSQL | Vertical / read replicas | RLS enforced, connection pooling recommended |
| Redis | Vertical / cluster mode | Used for cache, broker, rate limits |

---

## Monitoring & Health Checks

### Health Endpoint

```bash
curl http://localhost:8000/health
# {"status": "healthy", "version": "0.1.0"}
```

### Key Metrics to Monitor

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| API response time (p95) | API logs / APM | > 2s |
| API error rate (5xx) | API logs | > 1% |
| Celery task queue depth | Redis `celery` keys | > 1000 pending |
| Celery task failure rate | Celery events | > 5% |
| Token refresh failures | `token_vault.refresh_failure_count` | > 0 for any account |
| Connected account errors | `connected_accounts.status = 'error'` | Any |
| PostgreSQL connections | `pg_stat_activity` | > 80% of `max_connections` |
| Redis memory usage | `redis-cli info memory` | > 80% of `maxmemory` |
| Webhook processing lag | `webhook_events` where `status = 'received'` older than 5min | Any |
| Ad sync staleness | `ad_sync_cursors.last_synced_at` older than 2h | Any account |
| Content sync staleness | Video `updated_at` older than 24h with active account | Any |
| Intelligence sync staleness | `trend_snapshots` older than 8h | Any |
| Live session cleanup | `live_sessions` with `status = 'active'` older than 12h | Any |
| Messaging sync staleness | `conversations.last_synced_at` older than 2h | Any |
| Mention sync staleness | `brand_mentions` not updated in 4h | Any |
| Disk usage | OS metrics | > 85% |

### Log Locations

| Service | Log Source |
|---------|-----------|
| API | stdout (structured logging) |
| Celery Worker | stdout |
| Celery Beat | stdout |
| PostgreSQL | Docker: `docker compose logs postgres` |
| Redis | Docker: `docker compose logs redis` |

### Useful Log Queries

```bash
# API errors
docker compose logs api 2>&1 | grep "ERROR"

# Celery task failures
docker compose logs celery-worker 2>&1 | grep "Task .* raised"

# Webhook processing
docker compose logs celery-worker 2>&1 | grep "webhook"

# Token refresh issues
docker compose logs celery-worker 2>&1 | grep "token_refresh"

# Ad sync issues
docker compose logs celery-worker 2>&1 | grep "ad_sync"

# Content sync issues
docker compose logs celery-worker 2>&1 | grep "content_sync"

# Intelligence sync issues
docker compose logs celery-worker 2>&1 | grep "intelligence_sync"

# Live stream monitoring
docker compose logs celery-worker 2>&1 | grep "live_sync"

# Messaging sync
docker compose logs celery-worker 2>&1 | grep "messaging_sync"
```

---

## Common Issues & Fixes

### 1. Database connection refused

**Symptoms:** `asyncpg.exceptions.ConnectionDoesNotExistError` or connection timeout

**Diagnosis:**
```bash
docker compose ps postgres          # Check if running
docker compose logs postgres        # Check for errors
docker compose exec postgres pg_isready -U frodo
```

**Fix:**
```bash
docker compose restart postgres
# Wait for healthcheck to pass, then restart API
docker compose restart api
```

### 2. Redis connection failed

**Symptoms:** `redis.exceptions.ConnectionError`

**Diagnosis:**
```bash
docker compose ps redis
docker compose exec redis redis-cli ping   # Should return PONG
```

**Fix:**
```bash
docker compose restart redis
```

### 3. Celery workers not processing tasks

**Symptoms:** Tasks accumulate in queue, no progress

**Diagnosis:**
```bash
docker compose logs celery-worker --tail=50
# Check if worker is connected to broker
docker compose exec redis redis-cli llen celery  # Queue depth
```

**Fix:**
```bash
docker compose restart celery-worker
# If persistent, check CELERY_BROKER_URL in .env
```

### 4. Token refresh failures

**Symptoms:** Connected accounts show `status=error`, users can't perform platform operations

**Diagnosis:**
```sql
-- Check failed refreshes
SELECT ca.platform, ca.platform_user_name, tv.refresh_failure_count, tv.last_refresh_error
FROM connected_accounts ca
JOIN token_vault tv ON tv.connected_account_id = ca.id
WHERE tv.refresh_failure_count > 0;
```

**Fix:**
- If TikTok API is down: Wait and retry (automatic with backoff)
- If token expired beyond refresh window: User must re-authorize via `/connect/{platform}/authorize`
- Reset failure counter after fix:
  ```sql
  UPDATE token_vault SET refresh_failure_count = 0, last_refresh_error = NULL
  WHERE connected_account_id = '<id>';
  ```

### 5. Webhook signature verification failing

**Symptoms:** `webhook_events.signature_valid = false`

**Diagnosis:**
```sql
SELECT platform, event_type, signature_valid, received_at
FROM webhook_events
WHERE signature_valid = false
ORDER BY received_at DESC
LIMIT 20;
```

**Fix:**
- Verify app secrets match TikTok dashboard values
- Check for body encoding issues (raw bytes vs. decoded string)
- Shop: Verify HMAC-SHA256 with `app_key + raw_body`
- Developer: Verify timestamp-based `HMAC-SHA256(client_secret, timestamp.body)`

### 6. Alembic migration conflicts

**Symptoms:** `alembic upgrade head` fails with revision conflicts

**Fix:**
```bash
# Check current revision
alembic current

# Show migration history
alembic history

# If heads diverged, merge them
alembic merge heads -m "merge migrations"
alembic upgrade head
```

### 7. Rate limit exhaustion (TikTok APIs)

**Symptoms:** 429 responses from TikTok, operations failing

**Diagnosis:**
```bash
# Check rate limiter state in Redis
docker compose exec redis redis-cli keys "rate_limit:*"
```

**Fix:**
- The built-in rate limiter (Redis token bucket) should prevent this
- If hit: reduce concurrency in Celery workers
- Platform limits: Shop=50 QPS, Developer=600/min, Marketing=varies
- Check for runaway sync tasks or duplicate workers

### 8. Docker build fails

**Symptoms:** `pip install` fails in Docker build

**Fix:**
```bash
# Rebuild without cache
docker compose build --no-cache api

# Check pyproject.toml for version conflicts
pip install -e ".[dev]" --dry-run
```

### 9. Ad sync data stale

**Symptoms:** Campaign/ad group/ad data not updating in dashboard

**Diagnosis:**
```sql
SELECT ad_account_id, entity_type, last_synced_at, cursor_value
FROM ad_sync_cursors
ORDER BY last_synced_at;
```

**Fix:**
- Trigger manual sync: `POST /api/ads/campaigns/sync`
- Check Celery beat is running (scheduler for periodic sync)
- Check Marketing API token is still valid

### 10. Content publish job stuck

**Symptoms:** Publish job stays in `PROCESSING` status

**Diagnosis:**
```sql
SELECT id, status, publish_id, error_message, created_at
FROM content_publish_jobs
WHERE status = 'PROCESSING'
ORDER BY created_at DESC;
```

**Fix:**
- Check publish status via `GET /api/content/publish/{publish_id}/status`
- TikTok processing can take up to 15 minutes for video encoding
- If stuck > 30min, check Developer API token validity

### 11. Intelligence data not updating

**Symptoms:** Trends or competitor data is stale

**Diagnosis:**
```sql
SELECT category, collected_at FROM trend_snapshots ORDER BY collected_at DESC LIMIT 5;
SELECT tracker_id, last_synced_at FROM competitor_content ORDER BY last_synced_at DESC LIMIT 5;
```

**Fix:**
- Check `intelligence_sync` worker logs
- Verify Research API credentials are valid
- Trigger manual sync via intelligence endpoints

### 12. Live session stuck as active

**Symptoms:** Session shows as `active` but stream ended

**Diagnosis:**
```sql
SELECT id, stream_id, status, started_at FROM live_sessions
WHERE status = 'active' AND started_at < NOW() - INTERVAL '12 hours';
```

**Fix:**
- `cleanup_stale_sessions` task runs hourly to close stale sessions
- Manual: `PATCH /api/live/sessions/{id}` with `status: ended`

---

## Rollback Procedures

### Application Rollback

1. Identify the last known good image tag/commit:
   ```bash
   docker images frodo-api --format "{{.Tag}} {{.CreatedAt}}" | head -5
   ```

2. Deploy the previous image version.

3. If the bad deployment included migrations, rollback:
   ```bash
   # Check current migration
   alembic current

   # Rollback one step
   alembic downgrade -1

   # Rollback to specific revision
   alembic downgrade <revision_id>
   ```

4. Verify health:
   ```bash
   curl https://<api-host>/health
   ```

### Database Rollback

```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Check current state
alembic current
```

**Warning:** Data-destructive migrations (DROP TABLE, DROP COLUMN) cannot be fully rolled back. Always backup before applying such migrations:

```bash
docker compose exec postgres pg_dump -U frodo frodo > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Emergency: Full Database Restore

```bash
# Stop API and workers
docker compose stop api celery-worker celery-beat

# Restore from backup
docker compose exec -T postgres psql -U frodo frodo < backup_YYYYMMDD_HHMMSS.sql

# Run migrations to reach current state
docker compose exec api alembic upgrade head

# Restart services
docker compose start api celery-worker celery-beat
```

---

## Scheduled Tasks (Celery Beat)

| Task | Schedule | Worker File | Description |
|------|----------|-------------|-------------|
| Token refresh (Developer) | Every 12h | `token_refresh.py` | Refresh OAuth access tokens (24h expiry) |
| Token refresh (Shop) | Every 24h | `token_refresh.py` | Refresh Shop access tokens (7d expiry) |
| Token health check (Marketing) | Daily | `token_refresh.py` | Verify long-term Marketing tokens |
| Data sync (orders) | Every 5-15 min | `data_sync.py` | Polling fallback for missed webhooks |
| Data sync (products) | Every 15 min | `data_sync.py` | Reconcile product catalog |
| Ad account sync | Every 6h | `ad_sync.py` | Sync ad account list and status |
| Campaign sync | Every 30 min | `ad_sync.py` | Sync campaign data from Marketing API |
| Ad group sync | Every 30 min | `ad_sync.py` | Sync ad group data |
| Ad sync | Every 30 min | `ad_sync.py` | Sync individual ad data |
| Video sync | Every 1h | `content_sync.py` | Sync videos from Developer API |
| Video metrics sync | Every 6h | `content_sync.py` | Fetch updated video metrics |
| Creator metrics sync | Every 12h | `creator_sync.py` | Update creator follower/engagement data |
| Analytics aggregation | Every 1h | `analytics_sync.py` | Aggregate cross-platform KPIs |
| Daily KPI snapshot | Every 24h | `analytics_sync.py` | Record daily KPI snapshot |
| Scheduled reports | Every 6h | `analytics_sync.py` | Run user-defined scheduled reports |
| Trend sync | Every 4h | `intelligence_sync.py` | Sync trending hashtags/sounds from Research API |
| Competitor content sync | Every 6h | `intelligence_sync.py` | Track competitor content updates |
| Live stream monitor | On-demand | `live_sync.py` | Monitor active live streams |
| Live analytics compute | On completion | `live_sync.py` | Compute analytics after stream ends |
| Stale session cleanup | Every 1h | `live_sync.py` | Close stale live sessions |
| Conversation sync | Every 30 min | `messaging_sync.py` | Sync messaging conversations |
| Mention sync | Every 2h | `messaging_sync.py` | Sync brand mentions from organic |

---

## Security Operations

### Rotating Secrets

1. **JWT_SECRET_KEY**: Rotate by setting new value. All existing tokens invalidate immediately. Users must re-login.

2. **TOKEN_VAULT_KEY**: Requires re-encrypting all stored tokens. **Do not change without a migration script.**

3. **TikTok App Secrets**: Update in `.env` and restart services. Webhook verification will fail during the transition.

### Security Scanning

```bash
# Static analysis
bandit -r backend/

# Dependency vulnerabilities
pip audit
```

### Access Audit

```sql
-- Recent audit log entries
SELECT action, resource_type, user_id, ip_address, created_at
FROM audit_log
ORDER BY created_at DESC
LIMIT 50;

-- Failed login attempts (if logged)
SELECT * FROM audit_log
WHERE action = 'login_failed'
ORDER BY created_at DESC;
```

---

## Staleness Review

| File | Last Modified | Status |
|------|--------------|--------|
| `docs/CONTRIB.md` | 2026-02-23 | Updated |
| `docs/RUNBOOK.md` | 2026-02-23 | Updated |
| `docs/api-integration-manual.md` | 2026-02-22 | Current |
