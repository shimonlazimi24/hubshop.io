# Codebase Hygiene & Readiness Review Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Review all recent changes (20+ commits for multi-platform views feature), update all docs/codemaps, clean up untracked files and dead code, run full verification, and leave the codebase ready for next implementation phases.

**Architecture:** Multi-agent team operating in parallel where possible. Five workstreams: (1) Code Review of recent changes, (2) Test Suite Verification, (3) Documentation & Codemaps Update, (4) Cleanup & Formatting, (5) Security Scan. The team lead orchestrates, dispatches agents, and handles the final commit.

**Tech Stack:** Python 3.12 / FastAPI / Next.js 15 / pytest / black / isort / ruff / bandit

---

## Pre-Flight: Current State Assessment

### Untracked files requiring triage:
| File | Status | Action |
|------|--------|--------|
| `.claude/` | Claude Code project config | Add to `.gitignore` if not already |
| `backend/modules/content/routes/bridge.py` | New content-creator bridge routes | Review + commit |
| `backend/modules/content/services/content_creator_bridge.py` | New bridge service | Review + commit |
| `tests/unit/content/test_content_creator_bridge.py` | Tests for bridge (8 tests) | Review + commit |
| `docs/plans/2026-02-23-platform-tabs-layout-refactor-plan.md` | Completed plan doc | Commit |
| `knowledge-base/Githubrepors` | Research file with typo filename | Rename to `knowledge-base/github-repos-research.md` + commit |

### Recent changes to review (20 commits):
- Multi-platform views: `source_platform` field on advertising/commerce schemas
- `UnifiedCommerceService` and `UnifiedAdvertisingService` for cross-platform aggregation
- `PlatformTabs` component + `PlatformTabLayout` shared component
- `usePlatformFilter` hook (URL-driven platform state)
- Platform tabs in ads/commerce layouts with tab filtering
- Refactored ads/commerce pages to read platform from URL
- Frontend API client updated with platform param
- CODEMAPS/CONTRIB/RUNBOOK last generated

### Potential staleness in docs:
- CODEMAPS don't mention `ContentCreatorBridge`, `PlatformTabLayout` changes
- `CONTRIB.md` test count says 878 — may not reflect new bridge tests
- `MEMORY.md` needs multi-platform views feature noted as complete
- `ARCHITECTURE.md` doesn't mention multi-platform / unified services

---

## Task 1: Run Full Test Suite

**Purpose:** Establish green baseline before any changes.

**Step 1: Run backend tests**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/ -v --tb=short -q 2>&1 | tail -30`

Expected: All tests pass (878+ existing + 8 new bridge tests if tracked).

**Step 2: Run frontend build**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo/frontend" && npx next build 2>&1 | tail -20`

Expected: Build succeeds.

**Step 3: Record results**

Note exact pass count and any failures. If failures exist, they become blocking tasks before proceeding.

---

## Task 2: Code Review — Recent Changes (20 commits)

**Agent:** `code-reviewer` subagent

**Scope:** Review all changes since commit `8d4d6d0` (the multi-platform views plan commit) through `567ce8e` (latest).

**Files to review:**
- `backend/modules/advertising/schemas.py` — `source_platform` field additions
- `backend/modules/commerce/schemas.py` — `source_platform` field additions
- `backend/modules/commerce/services/unified_commerce.py` — `UnifiedCommerceService`
- `backend/modules/advertising/services/unified_advertising.py` — `UnifiedAdvertisingService`
- `frontend/src/components/ui/platform-tabs.tsx` — `PlatformTabs` component
- `frontend/src/components/ui/platform-tab-layout.tsx` — `PlatformTabLayout` shared component
- `frontend/src/hooks/usePlatformFilter.ts` — URL-driven platform hook
- `frontend/src/app/(dashboard)/ads/layout.tsx` — refactored ads layout
- `frontend/src/app/(dashboard)/commerce/layout.tsx` — refactored commerce layout
- `frontend/src/app/(dashboard)/ads/page.tsx` — platform filter from URL
- `frontend/src/app/(dashboard)/commerce/page.tsx` — platform filter from URL
- `frontend/src/lib/api.ts` — platform param additions
- All modified ads/commerce sub-pages (ad-groups, audiences, catalogs, pixels, products, returns, etc.)

**Review checklist:**
- [ ] No hardcoded strings that should be constants
- [ ] Type annotations complete on all Python functions
- [ ] No unused imports or dead code from refactoring
- [ ] Error handling covers edge cases
- [ ] API client changes backward-compatible
- [ ] `source_platform` properly optional (not breaking existing data)
- [ ] PlatformTabLayout properly abstracts the pattern (DRY)
- [ ] usePlatformFilter handles edge cases (missing param, invalid values)
- [ ] No console.log or print() left in production code

**Step 1: Run review**

The code-reviewer agent reads all files above and produces a report with CRITICAL / HIGH / MEDIUM findings.

**Step 2: Record findings**

Save findings to `.reports/code-review-hygiene.md`.

---

## Task 3: Code Review — Untracked Bridge Module

**Agent:** `code-reviewer` subagent (can run in parallel with Task 2)

**Files:**
- `backend/modules/content/routes/bridge.py`
- `backend/modules/content/services/content_creator_bridge.py`
- `tests/unit/content/test_content_creator_bridge.py`

**Review checklist:**
- [ ] Bridge routes registered in `backend/main.py` or content router
- [ ] Proper workspace_id tenant isolation on all queries
- [ ] `request_spark_ad_for_video` uses flush not commit (service layer pattern)
- [ ] Tests mock correctly (no real DB calls)
- [ ] Type annotations on all functions
- [ ] Response models used consistently
- [ ] No N+1 query patterns

**Step 1: Run review**

**Step 2: Check if bridge routes are registered**

Run: `grep -r "bridge" backend/modules/content/routes/__init__.py backend/main.py 2>/dev/null`

If NOT registered, this is a CRITICAL finding — routes exist but aren't mounted.

**Step 3: Record findings**

---

## Task 4: Security Review

**Agent:** `security-reviewer` subagent (can run in parallel with Tasks 2-3)

**Scope:** Scan recent changes + bridge module for security issues.

**Focus areas:**
- `ContentCreatorBridge` — SQL injection via raw queries? (should be using SQLAlchemy ORM — verify)
- `bridge.py` routes — auth dependency applied? (`CurrentUser` present on all endpoints)
- `api.ts` — any credential leakage in platform param handling?
- Token handling in unified services
- No secrets in committed files

**Step 1: Run bandit on backend**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && bandit -r backend/ -f json 2>/dev/null | python -m json.tool | head -50`

**Step 2: Check for secrets in untracked files**

Run: `grep -rn "password\|secret\|api_key\|token" backend/modules/content/routes/bridge.py backend/modules/content/services/content_creator_bridge.py`

Expected: No hardcoded secrets.

**Step 3: Record findings**

---

## Task 5: Cleanup — Rename Typo File

**Files:**
- Rename: `knowledge-base/Githubrepors` → `knowledge-base/github-repos-research.md`

**Step 1: Rename the file**

Run: `mv "/Users/amitkolton/Projects/Tiktok Frodo/knowledge-base/Githubrepors" "/Users/amitkolton/Projects/Tiktok Frodo/knowledge-base/github-repos-research.md"`

**Step 2: Verify**

Run: `ls "/Users/amitkolton/Projects/Tiktok Frodo/knowledge-base/github-repos-research.md"`

---

## Task 6: Cleanup — Formatting & Linting

**Step 1: Run black on backend + tests**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m black backend/ tests/ --check 2>&1 | tail -10`

If files need formatting:

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m black backend/ tests/`

**Step 2: Run isort**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m isort backend/ tests/ --check 2>&1 | tail -10`

If imports need sorting:

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m isort backend/ tests/`

**Step 3: Run ruff**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m ruff check backend/ tests/ 2>&1 | tail -20`

Fix any issues:

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m ruff check --fix backend/ tests/`

**Step 4: Run frontend lint**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo/frontend" && npm run lint 2>&1 | tail -20`

**Step 5: Record any remaining issues that need manual fixes**

---

## Task 7: Update CODEMAPS

**Agent:** `doc-updater` subagent

**Files to update:**
- `docs/CODEMAPS/architecture.md`
- `docs/CODEMAPS/backend.md`
- `docs/CODEMAPS/frontend.md`
- `docs/CODEMAPS/data.md`

**What's missing from current CODEMAPS:**

### architecture.md updates needed:
- Update UI component count: 20 → verify actual count
- Update test count: 878 → actual count after running tests
- Mention multi-platform views feature in Module Map description
- Add `UnifiedCommerceService` and `UnifiedAdvertisingService` to module descriptions
- Note `ContentCreatorBridge` as cross-module service (content ↔ creators)

### backend.md updates needed:
- Under `modules/content/`, add: `routes/bridge.py` and `services/content_creator_bridge.py`
- Update test count table to reflect actual numbers
- Note unified services pattern: `commerce/services/unified_commerce.py`, `advertising/services/unified_advertising.py`

### frontend.md updates needed:
- Verify component count matches actual (PlatformTabLayout was recently added)
- Note `PlatformTabLayout` as a layout pattern component
- Update hook count if needed (usePlatformFilter already listed)
- Update API Client line count if it grew with platform param additions

### data.md updates needed:
- Add `source_platform` field to Campaign model description
- Add `source_platform` field to Order/Product model descriptions (if added)
- Verify model count matches actual

**Step 1: Read current files and verify counts**

Run actual file counts:
```bash
find backend/ -name "*.py" -not -path "*/__pycache__/*" | wc -l
find frontend/src/components/ui/ -name "*.tsx" | wc -l
find frontend/src/app/\(dashboard\)/ -name "page.tsx" | wc -l
```

**Step 2: Update each CODEMAP file with accurate numbers and new entries**

**Step 3: Set freshness date to 2026-02-23**

---

## Task 8: Update CONTRIB.md

**Files:**
- Modify: `docs/CONTRIB.md`

**Updates needed:**
- Update test count (line 115: currently says 878)
- Update test coverage table if module counts changed
- Verify all available scripts are listed
- Add any new test markers if applicable

**Step 1: Get actual test count**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/ --co -q 2>&1 | tail -5`

**Step 2: Update CONTRIB.md with actual count**

---

## Task 9: Update MEMORY.md

**Files:**
- Modify: `/Users/amitkolton/.claude/projects/-Users-amitkolton-Projects-Tiktok-Frodo/memory/MEMORY.md`

**Updates needed:**
- Add "Multi-Platform Views" to Implementation Phases Summary table
- Note PlatformTabLayout pattern in Architecture Patterns section
- Update "Current Scale" test count
- Note ContentCreatorBridge as cross-module service
- Note unified services (UnifiedCommerceService, UnifiedAdvertisingService)
- Update frontend component count if changed

**Step 1: Read current MEMORY.md**

**Step 2: Add multi-platform views phase entry**

Add to Implementation Phases Summary:
```
| MPV | Multi-Platform Views | PlatformTabLayout, usePlatformFilter, source_platform fields, unified services |
```

**Step 3: Update Key Architecture Patterns**

Add:
```
- `frontend/src/components/ui/platform-tab-layout.tsx` = Shared PlatformTabLayout (platform tabs → feature tabs → content)
- `backend/modules/content/services/content_creator_bridge.py` = Cross-module bridge (content ↔ creators, Spark Ads)
- `backend/modules/*/services/unified_*.py` = Unified cross-platform aggregation services
```

---

## Task 10: Verify Bridge Module Registration

**Purpose:** The content creator bridge routes must be registered in the app to be accessible.

**Step 1: Check if bridge router is mounted**

Search for bridge imports in:
- `backend/modules/content/routes/__init__.py`
- `backend/main.py`

**Step 2: If NOT registered, add the bridge router**

In the content routes init or main.py, mount the bridge router:
```python
from backend.modules.content.routes.bridge import router as bridge_router
# Mount with prefix
app.include_router(bridge_router, prefix="/api/content", tags=["content-creator-bridge"])
```

**Step 3: Run tests to verify registration doesn't break anything**

Run: `python -m pytest tests/ -v --tb=short -q 2>&1 | tail -10`

---

## Task 11: Final Verification

**Step 1: Run full backend test suite**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m pytest tests/ -v --tb=short -q`

Expected: All tests pass.

**Step 2: Run frontend build**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo/frontend" && npx next build`

Expected: Build succeeds.

**Step 3: Run linters one more time**

Run: `cd "/Users/amitkolton/Projects/Tiktok Frodo" && python -m black backend/ tests/ --check && python -m isort backend/ tests/ --check && python -m ruff check backend/ tests/`

Expected: All clean.

**Step 4: Git status check**

Run: `git status`

Verify: No unexpected untracked files. All changes staged and ready.

---

## Task 12: Commit All Hygiene Changes

**Step 1: Stage all changes in logical groups**

```bash
# Group 1: New bridge module
git add backend/modules/content/routes/bridge.py
git add backend/modules/content/services/content_creator_bridge.py
git add tests/unit/content/test_content_creator_bridge.py

# Group 2: Renamed research file
git add knowledge-base/github-repos-research.md

# Group 3: Updated docs
git add docs/CODEMAPS/ docs/CONTRIB.md docs/RUNBOOK.md

# Group 4: Plan doc
git add docs/plans/2026-02-23-platform-tabs-layout-refactor-plan.md
git add docs/plans/2026-02-23-codebase-hygiene-plan.md

# Group 5: Any formatting/lint fixes
git add -p  # Review each change
```

**Step 2: Create commit**

```bash
git commit -m "chore: codebase hygiene — bridge module, docs update, cleanup"
```

**Step 3: Verify clean state**

Run: `git status`

Expected: Clean working directory (except `.claude/` if gitignored).

---

## Agent Orchestration Plan

### Parallel Wave 1 (Tasks 1, 2, 3, 4 — all independent):
| Agent | Task | Type | Est. Time |
|-------|------|------|-----------|
| **test-runner** | Task 1: Run test suite | `Bash` | 2 min |
| **reviewer-1** | Task 2: Review recent 20 commits | `code-reviewer` | 3 min |
| **reviewer-2** | Task 3: Review bridge module | `code-reviewer` | 2 min |
| **security** | Task 4: Security scan | `security-reviewer` | 2 min |

### Sequential Wave 2 (after Wave 1 completes — needs review findings):
| Agent | Task | Type | Est. Time |
|-------|------|------|-----------|
| **lead** | Task 5: Rename typo file | Manual | 30 sec |
| **formatter** | Task 6: Formatting & linting | `Bash` | 1 min |

### Parallel Wave 3 (Tasks 7, 8, 9 — independent doc updates):
| Agent | Task | Type | Est. Time |
|-------|------|------|-----------|
| **doc-1** | Task 7: Update CODEMAPS | `doc-updater` | 3 min |
| **doc-2** | Task 8: Update CONTRIB.md | `doc-updater` | 1 min |
| **doc-3** | Task 9: Update MEMORY.md | `general-purpose` | 1 min |

### Sequential Wave 4 (depends on all previous):
| Agent | Task | Type | Est. Time |
|-------|------|------|-----------|
| **lead** | Task 10: Verify bridge registration | Manual check | 1 min |
| **lead** | Task 11: Final verification | `Bash` | 2 min |
| **lead** | Task 12: Commit | Manual | 1 min |

### Total estimated wall-clock time: ~8 minutes (with parallelism)
