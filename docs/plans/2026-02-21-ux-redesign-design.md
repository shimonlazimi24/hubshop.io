# Frodo UX Redesign — "Performance Cockpit"

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:writing-plans to create the implementation plan from this design.

**Goal:** Transform every module page into a premium, data-rich "performance cockpit" experience — making Frodo feel like a unified performance platform and creative library, not a developer dashboard.

**Identity:** Performance platform + creative library. TikTok-inspired energy (coral/cyan) with B2B SaaS sophistication.

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Target user | DTC brands first, scale to agencies/enterprise | Classic SaaS expansion path |
| Sidebar navigation | Keep as-is | Works well, not a pain point |
| Page-level UX | Complete overhaul | Core problem: pages lack clarity, data density, and workflow guidance |
| Visual quality bar | Custom premium | TikTok energy meets B2B sophistication — stand out from Triple Whale, Shopify, Linear |
| Data visualization | Equal priority to workflow clarity | Performance data informs action |
| Creative library | Performance-linked | Every creative shows its metrics — this is the product differentiator |
| Creative Hub | Top-level module + contextual views in Ads/Content | Unified view as first-class citizen, modules keep their contextual pages |
| SaaS infrastructure | Skip for now | Focus on making module pages world-class first |

---

## Architecture: The 3-Zone Page Layout

Every module page follows this consistent structure:

```
┌─────────────────────────────────────────────────────────┐
│  Page Header: Title + Description + Primary CTA         │
├─────────────────────────────────────────────────────────┤
│  Metric Bar: 4-6 contextual KPIs with sparklines        │
│  [Revenue ▲12%] [ROAS 3.2x] [Spend $4.2K] [CTR 2.1%]  │
├───────────────────────────────────────┬─────────────────┤
│                                       │                 │
│  Main Content Zone                    │  Insight Panel  │
│  ┌─────────────────────────────────┐  │  (collapsible)  │
│  │ FilterBar: search + filters     │  │                 │
│  ├─────────────────────────────────┤  │  AI Suggestions │
│  │                                 │  │  Quick Actions  │
│  │  DataTable / Grid / Content     │  │  Related Data   │
│  │                                 │  │  Help Tips      │
│  └─────────────────────────────────┘  │                 │
│  Pagination                           │                 │
├───────────────────────────────────────┴─────────────────┤
```

**Principles:**
- MetricBar is always contextual to the current page
- InsightPanel is collapsed by default on smaller screens, toggle-able
- Main Content Zone holds DataTable (most pages), visual grid (creatives), or forms (publish/create)
- Every empty state tells the user what to do next

---

## Component Library

### Core Components

| Component | Purpose |
|-----------|---------|
| `<MetricCard>` | KPI display: value, label, trend arrow (▲/▼), sparkline, period comparison. Loading/empty states. |
| `<MetricBar>` | Horizontal row of 3-6 MetricCards. Responsive grid. |
| `<DataTable>` | Sortable, filterable table. Column config, row action menu, bulk selection, pagination. Replaces all hand-coded tables. |
| `<FilterBar>` | Search input + filter dropdowns + date range picker + saved filters. Sits above DataTable. |
| `<InsightPanel>` | Collapsible right sidebar. AI suggestions, related data, quick actions. Slides in/out with animation. |
| `<StatusBadge>` | Consistent status indicators (active/paused/error/draft) with semantic colors. |
| `<EmptyState>` | Icon + message + description + primary CTA. Contextual per module. |
| `<ActionMenu>` | Three-dot dropdown for row-level actions (edit, duplicate, archive, delete). |
| `<ChartCard>` | Chart wrapper with title, time range selector, loading state. Supports line/bar/donut. |
| `<PageShell>` | Standard page wrapper enforcing the 3-zone layout. |
| `<Toast>` | Success/error/info notification toasts. Replaces all alert() calls. |
| `<Modal>` | Confirmation dialogs, detail views, forms. Accessible, animated. |
| `<CreativeCard>` | Thumbnail + format badge + performance metrics overlay. For Creative Hub grid view. |

### Design Tokens

**Semantic Colors (add to globals.css):**
- `--success`: #10B981 (emerald-500) — active, live, completed
- `--warning`: #F59E0B (amber-500) — needs attention, pacing
- `--danger`: #EF4444 (red-500) — errors, overspend, failures
- `--info`: #3B82F6 (blue-500) — informational, syncing

**Chart Palette** (6 colors for multi-series):
- coral (#FE2C55), purple (#7B68EE), cyan (#25F4EE), emerald (#10B981), amber (#F59E0B), blue (#3B82F6)

**Elevation System:**
- `shadow-card`: `0 1px 3px rgba(0,0,0,0.08)` — cards, metric cards
- `shadow-panel`: `0 4px 12px rgba(0,0,0,0.1)` — insight panel, modals
- `shadow-modal`: `0 8px 24px rgba(0,0,0,0.15)` — modal overlays

**Animation Tokens:**
- `duration-fast`: 150ms — hover states, toggles
- `duration-normal`: 250ms — panel slides, page transitions
- `duration-slow`: 400ms — modal open/close, chart animations

---

## New Module: Creative Hub

A new top-level sidebar item that serves as the unified creative library and performance tool.

### Pages

| Page | Description |
|------|-------------|
| **Library** (default) | All creative assets (videos, images, carousels) in one place. Visual grid with performance metrics overlay (CTR, engagement, ROAS). Toggle grid/table view. Sort by performance, filter by type/status/campaign. Click → detail modal with full metrics, campaign usage, AI insights. |
| **Performance** | Cross-creative analytics. Which formats perform best, fatigue detection, A/B comparison tool. Charts + tables. |
| **Generate** | Symphony AI tools: smart creative generation, text recommendations, smart fix. Workflow cards with results area. |

### How It Connects

- Ads module links to creatives ("View creative" on a campaign → Creative Hub detail)
- Content publishing workflow starts from Creative Hub ("Publish to TikTok")
- Organic also references creatives from the hub
- Creative detail shows: where used (campaigns, posts), full performance breakdown, AI insights (fatigue, optimization)

### What Changes

- Ads/creatives page becomes a **context-filtered view** of the Creative Hub (showing only ad creatives)
- Content/videos page becomes a **context-filtered view** (showing only published content)
- Creative Hub is the single source of truth; module pages are lenses into it

---

## Module-by-Module Redesign

### Overview (Dashboard Home)
- **MetricBar**: Cross-module top KPIs (Revenue, Ad Spend, ROAS, Content Views, Followers)
- **Main Content**: Action items feed ("3 campaigns need attention", "5 pending orders"), module health cards, recent activity
- **Insight Panel**: Today's recommendations, trending alerts, quick shortcuts

### Advertising (16 pages)
- **Campaigns List**: MetricBar (Spend, ROAS, CPA, Active count). DataTable with status badges, budget bar visualization, inline performance metrics. Row hover actions. Insight Panel: top performer highlights, budget pacing alerts.
- **Campaign Detail**: Campaign-specific MetricBar. ChartCard (performance over time, switchable metrics). Sub-tables for Ad Groups and Ads. Insight Panel: optimization suggestions.
- **Ad Groups / Ads**: Same pattern — MetricBar + filtered DataTable + Insight Panel.
- **Search Ads**: Keyword research tool with volume/competition/CPC in DataTable. Negative keyword chip management. Campaign health cards with progress bars.
- **Symphony AI**: Moves primarily to Creative Hub > Generate. Ads/symphony becomes a shortcut/redirect.
- **Split Tests / Leads / Identities / Change Log / Custom Conversions**: MetricBar + DataTable pattern. Each with contextual Insight Panel.
- **Reports**: ChartCards for key metrics + DataTable for detailed breakdowns. Date range selector. Export capabilities.

### Commerce (10 pages)
- **Orders**: MetricBar (Revenue, Orders, AOV, Refund Rate). DataTable with status timeline badges. Insight Panel: fulfillment velocity, return risk alerts.
- **Products**: Grid/table toggle. Grid shows product images with inventory status and revenue.
- **Finance**: ChartCards for revenue/settlements/transactions over time.

### Content (5 pages)
- **Videos**: Context-filtered view of Creative Hub (published content only). Grid-first with performance metrics.
- **Publish**: Links to Creative Hub > publish workflow. Or accessible via shortcut.
- **Calendar**: Calendar view with scheduled/published content dots. Click date → list of content.

### Creators (6 pages)
- **Discovery**: Visual creator cards (avatar, stats, niche tag). Sortable, filterable. Insight Panel: recommended creators.
- **Campaigns**: DataTable with status, creator count, content delivered, ROI.
- **Spark Ads**: Performance-linked — each authorized creative shows its ad metrics.

### Intelligence (5 pages)
- **Trends**: ChartCards for hashtag/sound/product trends. Visual timeline.
- **Competitors**: Comparison dashboard — your metrics vs competitors.
- **Research**: Query builder + results DataTable.

### Messaging (3 pages)
- **Conversations**: Chat-style list with unread badges. MetricBar: response time, active conversations, auto-reply rate.
- **Auto-Messages**: DataTable with delivery/response metrics per template.

### Organic (3 pages)
- **Overview**: Brand health MetricBar (reach, mentions, sentiment, follower growth).
- **Mentions**: Sentiment-tagged feed with engagement metrics. Insight Panel: trending themes.
- **Publish**: Shortcut to Creative Hub publish workflow.

### LIVE (4 pages)
- **Active Streams**: Real-time updating metrics. Viewer count sparklines.
- **History**: Performance DataTable with recording links, gift revenue, peak viewers.
- **Analytics**: Post-stream ChartCards with engagement timeline.

### Analytics (7 pages)
- **Overview**: Executive dashboard — cross-module KPIs. ChartCards per business function.
- **Reports**: Scheduled report management with preview/export.
- **Notifications**: Alert center with filtering and bulk actions.

---

## Implementation Strategy

### Phase 1: Component Library
Build all 13 core components + design tokens. This is the foundation everything depends on.

### Phase 2: Creative Hub
New top-level module — the signature feature. Library, Performance, Generate pages.

### Phase 3: Advertising Module Redesign
Largest module, most impact. Apply 3-zone layout to all 16 pages.

### Phase 4: Overview + Content + Commerce
Dashboard home, Content (now connected to Creative Hub), Commerce pages.

### Phase 5: Remaining Modules
Creators, Intelligence, Messaging, Organic, LIVE, Analytics — apply the pattern.

---

## Success Criteria

- Every module page follows the 3-zone layout (MetricBar + Main + InsightPanel)
- No more `alert()` calls — all feedback via Toast component
- Creative Hub is a unified view of all creative assets with performance metrics
- Data tables are sortable, filterable, and have bulk actions
- Empty states guide users to their next action
- Consistent StatusBadge colors across all modules
- Premium visual quality: shadows, animations, spacing, typography
