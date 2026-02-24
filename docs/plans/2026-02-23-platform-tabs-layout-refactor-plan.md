# Platform Tabs Layout Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move PlatformTabs above feature tabs in layouts so platform selection drives which feature tabs are visible, and child pages inherit the platform filter from the URL.

**Architecture:** PlatformTabs moves from individual pages into `ads/layout.tsx` and `commerce/layout.tsx`, rendered above the feature tab nav. Each feature tab gets a `platforms` array specifying which platforms it's available for. A shared `usePlatformFilter` hook reads/writes `?platform=` from the URL. When the selected platform changes and the current feature tab isn't available, the layout redirects to the first available tab.

**Tech Stack:** Next.js 15 App Router, TypeScript, `useSearchParams` / `useRouter`, existing `PlatformTabs` component.

---

## Platform-to-Feature Mapping

### Advertising

| Feature Tab | `marketing` | `shop` |
|---|---|---|
| Campaigns | yes | yes |
| Ad Groups | yes | no |
| Ads (Creatives) | yes | no |
| Reports | yes | no |
| Audiences | yes | no |
| Pixels | yes | no |
| Catalogs | yes | no |
| Automation | yes | no |
| Events | yes | no |
| Comments | yes | no |
| Search Ads | yes | no |
| Symphony AI | yes | no |
| Split Tests | yes | no |
| Leads | yes | no |
| Identities | yes | no |

- **"All Platforms"** → all 15 tabs visible (unified read-only view)
- **"TikTok Ads"** (`marketing`) → all 15 tabs (full actions)
- **"Shop Promotions"** (`shop`) → Campaigns only (full actions)

### Commerce

| Feature Tab | `shop` | `affiliate` |
|---|---|---|
| Orders | yes | yes |
| Products | yes | yes |
| Returns | yes | no |
| Affiliate | no | yes |
| Promotions | yes | no |
| Finance | yes | yes |
| Messages | yes | no |
| Analytics | yes | yes |

- **"All Platforms"** → all 8 tabs visible (unified read-only view)
- **"TikTok Shop"** (`shop`) → 7 tabs (all except Affiliate)
- **"Affiliates"** (`affiliate`) → 5 tabs (Orders, Products, Affiliate, Finance, Analytics)

---

### Task 1: Create `usePlatformFilter` hook

**Files:**
- Create: `frontend/src/hooks/usePlatformFilter.ts`
- Test: `frontend/src/hooks/__tests__/usePlatformFilter.test.ts` (manual verification — Next.js router mocking is heavy, verify in browser)

**Step 1: Write the hook**

```typescript
"use client";

import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { useCallback } from "react";

export function usePlatformFilter(defaultValue = "all") {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const platform = searchParams.get("platform") ?? defaultValue;

  const setPlatform = useCallback(
    (value: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (value === defaultValue) {
        params.delete("platform");
      } else {
        params.set("platform", value);
      }
      const qs = params.toString();
      router.push(qs ? `${pathname}?${qs}` : pathname);
    },
    [searchParams, router, pathname, defaultValue],
  );

  return { platform, setPlatform } as const;
}
```

**Step 2: Commit**

```bash
git add frontend/src/hooks/usePlatformFilter.ts
git commit -m "feat: add usePlatformFilter hook for URL-driven platform state"
```

---

### Task 2: Add `platforms` to ads layout tab config and render PlatformTabs

**Files:**
- Modify: `frontend/src/app/(dashboard)/ads/layout.tsx`

**Step 1: Add `platforms` field to each tab and add imports**

Add to the top of the file:

```typescript
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { PlatformTabs } from "@/components/ui/platform-tabs";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
```

Update the `TABS` array type and add `platforms` to each entry:

```typescript
const ADS_PLATFORM_TABS = [
  { key: "all", label: "All Platforms" },
  { key: "marketing", label: "TikTok Ads" },
  { key: "shop", label: "Shop Promotions" },
];

const TABS = [
  {
    href: "/ads",
    label: "Campaigns",
    icon: Megaphone,
    exact: ["/ads"],
    prefix: ["/ads/campaigns"],
    platforms: ["marketing", "shop"],       // ← available on both
  },
  {
    href: "/ads/ad-groups",
    label: "Ad Groups",
    icon: Layers,
    exact: [],
    prefix: ["/ads/ad-groups"],
    platforms: ["marketing"],               // ← marketing only
  },
  // ... same pattern for all remaining tabs — all are ["marketing"] only
];
```

Full `platforms` mapping for every tab:

| Tab | platforms |
|---|---|
| Campaigns | `["marketing", "shop"]` |
| Ad Groups | `["marketing"]` |
| Ads (Creatives) | `["marketing"]` |
| Reports | `["marketing"]` |
| Audiences | `["marketing"]` |
| Pixels | `["marketing"]` |
| Catalogs | `["marketing"]` |
| Automation | `["marketing"]` |
| Events | `["marketing"]` |
| Comments | `["marketing"]` |
| Search Ads | `["marketing"]` |
| Symphony AI | `["marketing"]` |
| Split Tests | `["marketing"]` |
| Leads | `["marketing"]` |
| Identities | `["marketing"]` |

**Step 2: Update the layout component**

```typescript
export default function AdsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { platform, setPlatform } = usePlatformFilter();

  // Filter tabs: "all" shows everything, otherwise filter by platform
  const visibleTabs = platform === "all"
    ? TABS
    : TABS.filter((tab) => tab.platforms.includes(platform));

  // If current path not in visible tabs, redirect to first visible tab
  const isCurrentPathVisible = visibleTabs.some(
    (tab) =>
      tab.exact.some((m) => pathname === m) ||
      tab.prefix.some((m) => pathname === m || pathname.startsWith(m + "/"))
  );

  // ... render with PlatformTabs above feature nav
```

The JSX becomes:

```tsx
return (
  <div>
    <PageHeader
      title="Advertising"
      description="Manage your TikTok ad campaigns, ad groups, and reporting."
    />

    <PlatformTabs
      tabs={ADS_PLATFORM_TABS}
      value={platform}
      onChange={setPlatform}
    />

    <div className="border-b border-gray-200 mb-6">
      <nav className="flex gap-1">
        {visibleTabs.map((tab) => {
          // ... existing tab rendering logic (unchanged)
        })}
      </nav>
    </div>

    {children}
  </div>
);
```

**Step 3: Handle redirect when current tab not visible**

Add a `useEffect` that redirects to the first visible tab when the current path doesn't match any visible tab:

```typescript
import { useEffect } from "react";

// Inside the component, after isCurrentPathVisible:
useEffect(() => {
  if (!isCurrentPathVisible && visibleTabs.length > 0) {
    const params = new URLSearchParams();
    if (platform !== "all") params.set("platform", platform);
    const qs = params.toString();
    const target = qs ? `${visibleTabs[0].href}?${qs}` : visibleTabs[0].href;
    router.push(target);
  }
}, [isCurrentPathVisible, visibleTabs, platform]);
```

Note: Need to also get `router` from `useRouter()`.

**Step 4: Run frontend build**

```bash
cd frontend && npx next build
```

Expected: Build succeeds.

**Step 5: Commit**

```bash
git add frontend/src/app/\(dashboard\)/ads/layout.tsx
git commit -m "feat: add PlatformTabs to ads layout with tab filtering"
```

---

### Task 3: Add `platforms` to commerce layout tab config and render PlatformTabs

**Files:**
- Modify: `frontend/src/app/(dashboard)/commerce/layout.tsx`

**Step 1: Same pattern as Task 2 but for commerce**

Add imports, `COMMERCE_PLATFORM_TABS`, and `platforms` field to each tab:

```typescript
const COMMERCE_PLATFORM_TABS = [
  { key: "all", label: "All Platforms" },
  { key: "shop", label: "TikTok Shop" },
  { key: "affiliate", label: "Affiliates" },
];
```

Platform mapping for each tab:

| Tab | platforms |
|---|---|
| Orders | `["shop", "affiliate"]` |
| Products | `["shop", "affiliate"]` |
| Returns | `["shop"]` |
| Affiliate | `["affiliate"]` |
| Promotions | `["shop"]` |
| Finance | `["shop", "affiliate"]` |
| Messages | `["shop"]` |
| Analytics | `["shop", "affiliate"]` |

**Step 2: Update layout component identical to Task 2 pattern**

- Add `usePlatformFilter()` hook
- Filter `visibleTabs` based on platform
- Add redirect `useEffect`
- Render `PlatformTabs` above feature nav

**Step 3: Run frontend build**

```bash
cd frontend && npx next build
```

**Step 4: Commit**

```bash
git add frontend/src/app/\(dashboard\)/commerce/layout.tsx
git commit -m "feat: add PlatformTabs to commerce layout with tab filtering"
```

---

### Task 4: Remove PlatformTabs from `ads/page.tsx` and use URL platform

**Files:**
- Modify: `frontend/src/app/(dashboard)/ads/page.tsx`

**Step 1: Remove PlatformTabs and local platform state**

Remove from the file:
- `PlatformTabs` import
- `ADS_PLATFORM_TABS` constant
- `const [platformFilter, setPlatformFilter] = useState("all");`
- The `<PlatformTabs ... />` JSX element

**Step 2: Read platform from URL instead**

Add:

```typescript
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
```

Replace `platformFilter` state with:

```typescript
const { platform: platformFilter } = usePlatformFilter();
```

All existing logic that uses `platformFilter` (API calls, column visibility, etc.) stays the same — it was already using the variable name `platformFilter`. The only difference is the source changes from `useState` to URL.

**Step 3: Remove platform onChange handlers**

Remove `setPlatformFilter` references from the page since the layout now controls platform switching.

Specifically, remove this line from `PlatformTabs onChange`:
```typescript
onChange={(v) => { setPlatformFilter(v); setPage(1); }}
```
This was on the PlatformTabs component that is now deleted from this page.

The `setPage(1)` reset should happen when platform changes. Add a `useEffect`:

```typescript
useEffect(() => {
  setPage(1);
}, [platformFilter]);
```

**Step 4: Remove `PageHeader` from page (layout already has it)**

The ads layout already renders `<PageHeader title="Advertising" ... />`. If the page has its own `<PageHeader>`, remove the duplicate. Keep the `Create Campaign` link as an action in the layout's `PageHeader` or move it to a `FilterBar` action.

Actually, looking at the current `ads/page.tsx`, it has its own `<PageHeader>` with a "Create Campaign" action button. This should be kept on the page (not the layout) since it's page-specific. So keep the `<PageHeader>` in the page but ensure there's no duplicate with the layout.

Check: the layout already has `<PageHeader title="Advertising" ...>`. The page has `<PageHeader title="Campaigns" ...>` with create button. These are different — the layout one is the module header, the page one is the sub-page header. Both should stay.

**Step 5: Run frontend build**

```bash
cd frontend && npx next build
```

**Step 6: Commit**

```bash
git add frontend/src/app/\(dashboard\)/ads/page.tsx
git commit -m "refactor: remove PlatformTabs from ads page, read platform from URL"
```

---

### Task 5: Remove PlatformTabs from `commerce/page.tsx` and use URL platform

**Files:**
- Modify: `frontend/src/app/(dashboard)/commerce/page.tsx`

**Step 1: Same pattern as Task 4 but for commerce**

Remove:
- `PlatformTabs` import
- `COMMERCE_PLATFORM_TABS` constant
- `const [platformFilter, setPlatformFilter] = useState("all");`
- `<PlatformTabs ... />` JSX

Replace with:

```typescript
import { usePlatformFilter } from "@/hooks/usePlatformFilter";

// In component:
const { platform: platformFilter } = usePlatformFilter();
```

Add page reset on platform change:

```typescript
useEffect(() => {
  setPage(1);
}, [platformFilter]);
```

**Step 2: Run frontend build**

```bash
cd frontend && npx next build
```

**Step 3: Commit**

```bash
git add frontend/src/app/\(dashboard\)/commerce/page.tsx
git commit -m "refactor: remove PlatformTabs from commerce page, read platform from URL"
```

---

### Task 6: Propagate platform to sub-pages that fetch data

**Files:**
- Modify: All sub-pages in `frontend/src/app/(dashboard)/ads/*/page.tsx` that make API calls
- Modify: All sub-pages in `frontend/src/app/(dashboard)/commerce/*/page.tsx` that make API calls

**Step 1: Identify which sub-pages fetch list data**

These pages call list endpoints and should pass the platform filter:

**Ads sub-pages** (14 pages):
- `ad-groups/page.tsx` → `listAdGroups`
- `creatives/page.tsx` → `listAds`
- `reports/page.tsx` → report endpoints
- `audiences/page.tsx` → `listAudiences`
- `pixels/page.tsx` → `listPixels`
- `catalogs/page.tsx` → `listCatalogs`
- Others: `automation`, `events`, `comments`, `search`, `symphony`, `split-tests`, `leads`, `identities`

**Commerce sub-pages** (7 pages):
- `products/page.tsx` → `listProducts`
- `returns/page.tsx` → `listReturns`
- `affiliate/page.tsx` → `listAffiliateProducts`
- `promotions/page.tsx` → promotions endpoint
- `finance/page.tsx` → finance endpoint
- `messages/page.tsx` → messages endpoint
- `analytics/page.tsx` → analytics endpoint

**Step 2: For each sub-page, add the hook**

Pattern (same for every sub-page):

```typescript
import { usePlatformFilter } from "@/hooks/usePlatformFilter";

// Inside component:
const { platform } = usePlatformFilter();

// Pass to API calls:
const platformParam = platform === "all" ? undefined : platform;
```

This is a mechanical change — add the import, read the hook, pass to API calls. The sub-pages don't need PlatformTabs (the layout handles that). They just need to know the current platform for data filtering.

**Note:** Many sub-pages are marketing-only (Ad Groups, Pixels, Audiences, etc.), so when platform is "marketing" the API call remains unchanged. When platform is "all", passing `undefined` returns all platforms. This is already handled by the backend.

**Step 3: Run frontend build**

```bash
cd frontend && npx next build
```

**Step 4: Commit**

```bash
git add frontend/src/app/\(dashboard\)/ads/ frontend/src/app/\(dashboard\)/commerce/
git commit -m "feat: propagate platform filter to all sub-pages"
```

---

### Task 7: Wrap layout children in Suspense boundary

**Files:**
- Modify: `frontend/src/app/(dashboard)/ads/layout.tsx`
- Modify: `frontend/src/app/(dashboard)/commerce/layout.tsx`

**Step 1: Add Suspense**

`useSearchParams()` in Next.js 15 App Router requires a `<Suspense>` boundary for static rendering. Wrap `{children}` in both layouts:

```typescript
import { Suspense } from "react";

// In JSX:
<Suspense fallback={null}>
  {children}
</Suspense>
```

Also wrap the layout component itself in Suspense if `useSearchParams` is used directly in the layout. The typical pattern:

```typescript
function AdsLayoutInner({ children }: { children: React.ReactNode }) {
  // All the logic with useSearchParams
  return ( /* JSX */ );
}

export default function AdsLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={null}>
      <AdsLayoutInner>{children}</AdsLayoutInner>
    </Suspense>
  );
}
```

**Step 2: Run frontend build**

```bash
cd frontend && npx next build
```

**Step 3: Commit**

```bash
git add frontend/src/app/\(dashboard\)/ads/layout.tsx frontend/src/app/\(dashboard\)/commerce/layout.tsx
git commit -m "fix: add Suspense boundary for useSearchParams in layouts"
```

---

### Task 8: End-to-end verification

**Step 1: Run full backend test suite**

```bash
cd backend && python -m pytest --tb=short -q
```

Expected: All tests pass (878+).

**Step 2: Run frontend build**

```bash
cd frontend && npx next build
```

Expected: Build succeeds with no errors.

**Step 3: Manual browser verification checklist**

1. Navigate to `/ads` → PlatformTabs appears ABOVE feature tabs
2. Select "Shop Promotions" → only "Campaigns" tab visible
3. Select "TikTok Ads" → all 15 tabs visible
4. Select "All Platforms" → all 15 tabs visible
5. On "TikTok Ads", navigate to Ad Groups → switch to "Shop Promotions" → auto-redirects to Campaigns
6. Navigate to `/commerce` → PlatformTabs appears ABOVE feature tabs
7. Select "Affiliates" → only Orders, Products, Affiliate, Finance, Analytics visible
8. Select "TikTok Shop" → all tabs except Affiliate visible
9. URL shows `?platform=shop` or `?platform=affiliate` as expected
10. Direct URL navigation with `?platform=marketing` works

**Step 4: Commit (if any fixes needed)**

```bash
git commit -m "fix: end-to-end verification fixes"
```
