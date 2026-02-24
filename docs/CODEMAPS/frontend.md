# Frodo Frontend Codemap

> Freshness: 2026-02-24 | Auto-generated

## Directory Structure

```
frontend/src/
  app/
    layout.tsx                # RootLayout (Geist font, metadata)
    page.tsx                  # Landing page (10 sections)
    (auth)/
      login/page.tsx          # LoginPage (email + social OAuth)
      register/page.tsx       # RegisterPage
      callback/page.tsx       # OAuth callback handler
    (dashboard)/
      layout.tsx              # DashboardLayout (sidebar, topbar, auth guard)
      overview/page.tsx       # KPI cockpit + quick actions
      connect/page.tsx        # Account connection hub
      settings/page.tsx       # Workspace settings
      commerce/               # 9 pages (layout + orders, products, returns, affiliate, analytics, finance, messages, promotions)
      ads/                    # 17 pages (layout + campaigns CRUD/wizard, ad-groups, creatives, reports, audiences, pixels, catalogs, automation, events, comments, search, symphony, split-tests, leads, identities)
      content/                # 5 pages (layout + videos, publish, calendar, analytics)
      creatives/              # 4 pages (layout + library, generate, performance)
      creators/               # 7 pages (layout + discovery, profiles, campaigns CRUD, spark-ads)
      intelligence/           # 6 pages (layout + trends, competitors, creators, research)
      live/                   # 5 pages (layout + monitor, sessions, analytics, history)
      messaging/              # 4 pages (layout + inbox, thread, auto-messages)
      organic/                # 4 pages (layout + mentions, publish)
      analytics/              # 8 pages (layout + overview, advertising, commerce, content, notifications, reports, settings)
  components/
    ui/                       # 20 reusable components
    dashboard/                # 6 layout components
    landing/                  # 10 marketing sections
  hooks/                      # 3 custom hooks
  lib/                        # 4 utility modules
  config/                     # Navigation config
```

## UI Components (20)

| Component | File | Key Props |
|-----------|------|-----------|
| ActionMenu | action-menu.tsx | items: { label, icon, onClick }[] |
| Badge | badge.tsx | variant, children |
| Button | button.tsx | variant, size, children |
| ChartCard | chart-card.tsx | title, timeRanges, children |
| CreativeCard | creative-card.tsx | creative asset preview |
| DataTable\<T\> | data-table.tsx | columns, data, keyExtractor, pagination, loading, empty state |
| EmptyState | empty-state.tsx | icon, title, description, action |
| FilterBar | filter-bar.tsx | searchValue, onSearchChange, actions, children (FilterDropdown) |
| InsightPanel | insight-panel.tsx | defaultOpen, children (InsightItem) |
| MetricBar | metric-bar.tsx | children (MetricCard grid) |
| MetricCard | metric-card.tsx | label, value, icon, iconColor, trend, sparklineData, loading |
| Modal | modal.tsx | open, onClose, title, children |
| PageShell | page-shell.tsx | header (MetricBar), aside (InsightPanel), children |
| PlatformTabs | platform-tabs.tsx | tabs, value, onChange |
| PlatformTabLayout | platform-tab-layout.tsx | title, description, platformTabs, featureTabs, children |
| Skeleton | skeleton.tsx | className |
| StatusBadge | status-badge.tsx | variant (active/draft/completed/error/syncing/warning), label |
| Tabs | tabs.tsx | compound component with context |
| Toast | toast.tsx | ToastContainer, auto-dismiss |
| Tooltip | tooltip.tsx | content, children |

## Custom Hooks (3)

| Hook | File | Returns |
|------|------|---------|
| `usePlatformFilter` | usePlatformFilter.ts | `{ platform, setPlatform }` - URL query param state |
| `useSidebarState` | useSidebarState.ts | `{ collapsed, toggle, collapse, expand }` - localStorage |
| `useCommerceWebSocket` | useCommerceWebSocket.ts | `{ connected }` - real-time order updates |

## Library Modules (4)

| Module | File | Key Exports |
|--------|------|-------------|
| API Client | api.ts (1638 lines) | 100+ functions, `apiFetch<T>`, all type definitions |
| Auth | auth.ts | getAccessToken, setTokens, clearTokens, isAuthenticated |
| Toast Store | toast-store.ts | `toast.success/error/info/warning`, useToasts |
| Utils | utils.ts | `cn()` (clsx + twMerge) |

## Dashboard Components (6)

| Component | File | Purpose |
|-----------|------|---------|
| Sidebar | sidebar.tsx | Collapsible nav, workspace switcher |
| TopBar | top-bar.tsx | Breadcrumbs, Cmd+K search, notifications |
| MobileNav | mobile-nav.tsx | Hamburger drawer menu |
| NotificationBell | notification-bell.tsx | Real-time notification dropdown |
| PageHeader | page-header.tsx | Title + description + actions |
| CommandPalette | command-palette.tsx | Cmd+K search with keyboard nav |

## Navigation Config

12 main items + settings in 3 groups:

| Group | Items |
|-------|-------|
| Main | Overview, Connect |
| Modules | Commerce, Advertising, Content, Creative Hub, Creators, LIVE, Messaging, Organic |
| Insights | Intelligence, Analytics |

## Layout Patterns

1. **3-Zone Performance Cockpit** (PageShell): MetricBar top + content center + InsightPanel right
2. **PlatformTabLayout**: Platform filter tabs -> filtered feature nav tabs -> page content
3. **DashboardLayout**: Sidebar + TopBar + CommandPalette + ToastContainer

## Design Tokens

- **Primary**: coral
- **Semantic**: success (green), warning (amber), danger (red), info (blue), purple
- **Shadows**: shadow-card, shadow-panel, shadow-modal
- **Animations**: Framer Motion fade/spring, 150ms transitions
