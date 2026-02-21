# UX Redesign "Performance Cockpit" Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform every module page into a premium 3-zone "performance cockpit" layout with a shared component library, unified Creative Hub, and data-rich UX.

**Architecture:** Build a reusable component library first (design tokens, MetricCard, DataTable, FilterBar, InsightPanel, etc.), then apply it to a new Creative Hub module, then systematically redesign all existing module pages using the components.

**Tech Stack:** Next.js 16 / React 19 / TypeScript / Tailwind CSS 4 / Framer Motion / Recharts (new) / Lucide React

**Design Doc:** `docs/plans/2026-02-21-ux-redesign-design.md`

---

## Phase 1: Design Tokens & Dependencies

### Task 1: Install charting dependency

**Files:**
- Modify: `frontend/package.json`

**Step 1: Install recharts**

```bash
cd frontend && npm install recharts
```

**Step 2: Verify it installs**

Run: `cd frontend && npx next build 2>&1 | tail -5`
Expected: Build succeeds (or at least no recharts import errors)

**Step 3: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "chore: add recharts dependency for chart components"
```

---

### Task 2: Add design tokens to globals.css

**Files:**
- Modify: `frontend/src/app/globals.css`

**Step 1: Add semantic colors, elevation, animation, and chart palette tokens**

Add these CSS variables and `@theme` entries after the existing ones in `globals.css`:

```css
/* --- Add to :root block, after existing variables --- */
  --success: #10B981;
  --warning: #F59E0B;
  --danger: #EF4444;
  --info: #3B82F6;

  /* Chart palette */
  --chart-1: #FE2C55;
  --chart-2: #7B68EE;
  --chart-3: #25F4EE;
  --chart-4: #10B981;
  --chart-5: #F59E0B;
  --chart-6: #3B82F6;

  /* Elevation */
  --shadow-card: 0 1px 3px rgba(0,0,0,0.08);
  --shadow-panel: 0 4px 12px rgba(0,0,0,0.1);
  --shadow-modal: 0 8px 24px rgba(0,0,0,0.15);

  /* Animation durations */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
```

Add to the `@theme inline` block:

```css
  --color-success: var(--success);
  --color-warning: var(--warning);
  --color-danger: var(--danger);
  --color-info: var(--info);
  --color-chart-1: var(--chart-1);
  --color-chart-2: var(--chart-2);
  --color-chart-3: var(--chart-3);
  --color-chart-4: var(--chart-4);
  --color-chart-5: var(--chart-5);
  --color-chart-6: var(--chart-6);
```

**Step 2: Verify Tailwind recognizes new tokens**

Run: `cd frontend && npx next build 2>&1 | tail -5`
Expected: Build succeeds — new colors like `text-success`, `bg-danger` now available.

**Step 3: Commit**

```bash
git add frontend/src/app/globals.css
git commit -m "feat: add semantic colors, elevation, animation, and chart design tokens"
```

---

## Phase 2: Core Component Library

All components go in `frontend/src/components/ui/`. Follow existing patterns: TypeScript, `cn()` utility, Tailwind classes, Lucide icons.

### Task 3: StatusBadge component

**Files:**
- Create: `frontend/src/components/ui/status-badge.tsx`

**Step 1: Create the component**

```tsx
"use client";

import { cn } from "@/lib/utils";

export type StatusVariant = "active" | "paused" | "error" | "draft" | "completed" | "syncing" | "warning";

const VARIANT_STYLES: Record<StatusVariant, string> = {
  active: "bg-success/10 text-success border-success/20",
  completed: "bg-success/10 text-success border-success/20",
  paused: "bg-gray-100 text-gray-600 border-gray-200",
  draft: "bg-gray-100 text-gray-500 border-gray-200",
  error: "bg-danger/10 text-danger border-danger/20",
  syncing: "bg-info/10 text-info border-info/20",
  warning: "bg-warning/10 text-warning border-warning/20",
};

const DOT_STYLES: Record<StatusVariant, string> = {
  active: "bg-success",
  completed: "bg-success",
  paused: "bg-gray-400",
  draft: "bg-gray-400",
  error: "bg-danger",
  syncing: "bg-info animate-pulse",
  warning: "bg-warning",
};

interface StatusBadgeProps {
  variant: StatusVariant;
  label?: string;
  className?: string;
}

export function StatusBadge({ variant, label, className }: StatusBadgeProps) {
  const displayLabel = label ?? variant.charAt(0).toUpperCase() + variant.slice(1);

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        VARIANT_STYLES[variant],
        className
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", DOT_STYLES[variant])} />
      {displayLabel}
    </span>
  );
}
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`
Expected: Build succeeds.

**Step 3: Commit**

```bash
git add frontend/src/components/ui/status-badge.tsx
git commit -m "feat: add StatusBadge component with 7 semantic variants"
```

---

### Task 4: MetricCard component

**Files:**
- Create: `frontend/src/components/ui/metric-card.tsx`

**Step 1: Create the component**

```tsx
"use client";

import type { LucideIcon } from "lucide-react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: LucideIcon;
  iconColor?: string;
  trend?: {
    value: number;       // e.g. 12.5 for +12.5%
    direction: "up" | "down" | "flat";
    label?: string;      // e.g. "vs last week"
  };
  sparklineData?: number[];
  loading?: boolean;
  className?: string;
}

function MiniSparkline({ data, className }: { data: number[]; className?: string }) {
  if (data.length < 2) return null;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const h = 24;
  const w = 64;
  const step = w / (data.length - 1);

  const points = data
    .map((v, i) => `${i * step},${h - ((v - min) / range) * h}`)
    .join(" ");

  return (
    <svg width={w} height={h} className={cn("text-coral", className)} viewBox={`0 0 ${w} ${h}`}>
      <polyline
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  );
}

export function MetricCard({
  label,
  value,
  icon: Icon,
  iconColor = "text-coral",
  trend,
  sparklineData,
  loading = false,
  className,
}: MetricCardProps) {
  const TrendIcon =
    trend?.direction === "up"
      ? TrendingUp
      : trend?.direction === "down"
      ? TrendingDown
      : Minus;

  const trendColor =
    trend?.direction === "up"
      ? "text-success"
      : trend?.direction === "down"
      ? "text-danger"
      : "text-gray-400";

  return (
    <div
      className={cn(
        "rounded-xl border border-gray-100 bg-white p-5 shadow-[var(--shadow-card)] transition-shadow duration-[var(--duration-fast)] hover:shadow-[var(--shadow-panel)]",
        className
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</p>
        {Icon && (
          <div className={cn("flex h-8 w-8 items-center justify-center rounded-lg bg-gray-50", iconColor)}>
            <Icon className="h-4 w-4" />
          </div>
        )}
      </div>

      {loading ? (
        <Skeleton className="h-8 w-24 mb-2" />
      ) : (
        <p className="text-2xl font-bold text-gray-900 tabular-nums">
          {typeof value === "number" ? value.toLocaleString() : value}
        </p>
      )}

      <div className="flex items-center justify-between mt-2">
        {trend && !loading ? (
          <span className={cn("flex items-center gap-1 text-xs font-medium", trendColor)}>
            <TrendIcon className="h-3 w-3" />
            {trend.direction !== "flat" && (
              <span>{trend.direction === "up" ? "+" : ""}{trend.value}%</span>
            )}
            {trend.label && <span className="text-gray-400 ml-1">{trend.label}</span>}
          </span>
        ) : (
          <span />
        )}
        {sparklineData && !loading && <MiniSparkline data={sparklineData} />}
      </div>
    </div>
  );
}
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`
Expected: Build succeeds.

**Step 3: Commit**

```bash
git add frontend/src/components/ui/metric-card.tsx
git commit -m "feat: add MetricCard component with trend indicators and sparklines"
```

---

### Task 5: MetricBar component

**Files:**
- Create: `frontend/src/components/ui/metric-bar.tsx`

**Step 1: Create the component**

```tsx
import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

interface MetricBarProps {
  children: ReactNode;
  className?: string;
}

export function MetricBar({ children, className }: MetricBarProps) {
  return (
    <div
      className={cn(
        "grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4 mb-6",
        className
      )}
    >
      {children}
    </div>
  );
}
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`
Expected: Build succeeds.

**Step 3: Commit**

```bash
git add frontend/src/components/ui/metric-bar.tsx
git commit -m "feat: add MetricBar responsive grid wrapper"
```

---

### Task 6: ActionMenu component

**Files:**
- Create: `frontend/src/components/ui/action-menu.tsx`

**Step 1: Create the component**

```tsx
"use client";

import { useState, useRef, useEffect, type ReactNode } from "react";
import { MoreHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";

interface ActionItem {
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  variant?: "default" | "danger";
  disabled?: boolean;
}

interface ActionMenuProps {
  items: ActionItem[];
  className?: string;
}

export function ActionMenu({ items, className }: ActionMenuProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  return (
    <div ref={ref} className={cn("relative", className)}>
      <button
        onClick={(e) => {
          e.stopPropagation();
          setOpen(!open);
        }}
        className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
      >
        <MoreHorizontal className="h-4 w-4" />
      </button>

      {open && (
        <div className="absolute right-0 top-full z-50 mt-1 min-w-[160px] rounded-lg border border-gray-200 bg-white py-1 shadow-[var(--shadow-panel)]">
          {items.map((item) => (
            <button
              key={item.label}
              disabled={item.disabled}
              onClick={(e) => {
                e.stopPropagation();
                item.onClick();
                setOpen(false);
              }}
              className={cn(
                "flex w-full items-center gap-2 px-3 py-2 text-sm transition-colors",
                item.variant === "danger"
                  ? "text-danger hover:bg-danger/5"
                  : "text-gray-700 hover:bg-gray-50",
                item.disabled && "opacity-50 cursor-not-allowed"
              )}
            >
              {item.icon && <span className="h-4 w-4">{item.icon}</span>}
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/components/ui/action-menu.tsx
git commit -m "feat: add ActionMenu dropdown component"
```

---

### Task 7: EmptyState component

**Files:**
- Create: `frontend/src/components/ui/empty-state.tsx`

**Step 1: Create the component**

```tsx
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Inbox } from "lucide-react";

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-16 px-4 text-center", className)}>
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gray-100 mb-4">
        <Icon className="h-6 w-6 text-gray-400" />
      </div>
      <h3 className="text-sm font-semibold text-gray-900 mb-1">{title}</h3>
      {description && (
        <p className="text-sm text-gray-500 max-w-sm mb-4">{description}</p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          className="inline-flex items-center gap-1.5 rounded-lg bg-coral px-4 py-2 text-sm font-medium text-white hover:bg-coral-dark transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/components/ui/empty-state.tsx
git commit -m "feat: add EmptyState component with icon, message, and CTA"
```

---

### Task 8: Toast notification system

**Files:**
- Create: `frontend/src/components/ui/toast.tsx`
- Create: `frontend/src/lib/toast-store.ts`

**Step 1: Create the toast store**

```tsx
// frontend/src/lib/toast-store.ts
"use client";

import { useSyncExternalStore } from "react";

export type ToastVariant = "success" | "error" | "info" | "warning";

export interface ToastItem {
  id: string;
  variant: ToastVariant;
  message: string;
  duration?: number;
}

let toasts: ToastItem[] = [];
let listeners: Array<() => void> = [];

function emit() {
  listeners.forEach((l) => l());
}

export function addToast(variant: ToastVariant, message: string, duration = 4000) {
  const id = crypto.randomUUID();
  toasts = [...toasts, { id, variant, message, duration }];
  emit();
  if (duration > 0) {
    setTimeout(() => removeToast(id), duration);
  }
}

export function removeToast(id: string) {
  toasts = toasts.filter((t) => t.id !== id);
  emit();
}

export function useToasts(): ToastItem[] {
  return useSyncExternalStore(
    (cb) => {
      listeners.push(cb);
      return () => {
        listeners = listeners.filter((l) => l !== cb);
      };
    },
    () => toasts,
    () => []
  );
}

// Convenience helpers
export const toast = {
  success: (msg: string) => addToast("success", msg),
  error: (msg: string) => addToast("error", msg),
  info: (msg: string) => addToast("info", msg),
  warning: (msg: string) => addToast("warning", msg),
};
```

**Step 2: Create the toast renderer component**

```tsx
// frontend/src/components/ui/toast.tsx
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useToasts, removeToast, type ToastVariant } from "@/lib/toast-store";

const ICON_MAP: Record<ToastVariant, typeof CheckCircle> = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
  warning: AlertTriangle,
};

const STYLE_MAP: Record<ToastVariant, string> = {
  success: "border-success/20 bg-success/5 text-success",
  error: "border-danger/20 bg-danger/5 text-danger",
  info: "border-info/20 bg-info/5 text-info",
  warning: "border-warning/20 bg-warning/5 text-warning",
};

export function ToastContainer() {
  const toasts = useToasts();

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm">
      <AnimatePresence>
        {toasts.map((t) => {
          const Icon = ICON_MAP[t.variant];
          return (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{ duration: 0.25 }}
              className={cn(
                "flex items-start gap-3 rounded-lg border bg-white px-4 py-3 shadow-[var(--shadow-panel)]"
              )}
            >
              <Icon className={cn("h-5 w-5 mt-0.5 flex-shrink-0", STYLE_MAP[t.variant])} />
              <p className="text-sm text-gray-700 flex-1">{t.message}</p>
              <button
                onClick={() => removeToast(t.id)}
                className="text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0"
              >
                <X className="h-4 w-4" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
```

**Step 3: Add ToastContainer to dashboard layout**

In `frontend/src/app/(dashboard)/layout.tsx`, add `<ToastContainer />` before the closing `</body>` or at the end of the layout's JSX (inside the outermost wrapper). Import from `@/components/ui/toast`.

**Step 4: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 5: Commit**

```bash
git add frontend/src/lib/toast-store.ts frontend/src/components/ui/toast.tsx frontend/src/app/\(dashboard\)/layout.tsx
git commit -m "feat: add Toast notification system with store and renderer"
```

---

### Task 9: Modal component

**Files:**
- Create: `frontend/src/components/ui/modal.tsx`

**Step 1: Create the component**

```tsx
"use client";

import { useEffect, type ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children: ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

const SIZE_MAP: Record<string, string> = {
  sm: "max-w-md",
  md: "max-w-lg",
  lg: "max-w-2xl",
  xl: "max-w-4xl",
};

export function Modal({
  open,
  onClose,
  title,
  description,
  children,
  size = "md",
  className,
}: ModalProps) {
  useEffect(() => {
    function handleEsc(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    if (open) {
      document.addEventListener("keydown", handleEsc);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEsc);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="absolute inset-0 bg-black/40"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.25 }}
            className={cn(
              "relative w-full rounded-2xl bg-white shadow-[var(--shadow-modal)]",
              SIZE_MAP[size],
              className
            )}
          >
            {/* Header */}
            {(title || description) && (
              <div className="flex items-start justify-between border-b border-gray-100 px-6 py-4">
                <div>
                  {title && <h2 className="text-lg font-semibold text-gray-900">{title}</h2>}
                  {description && <p className="text-sm text-gray-500 mt-0.5">{description}</p>}
                </div>
                <button
                  onClick={onClose}
                  className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}

            {/* Body */}
            <div className="px-6 py-4 max-h-[70vh] overflow-y-auto">
              {children}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/components/ui/modal.tsx
git commit -m "feat: add Modal component with backdrop, animations, and size variants"
```

---

### Task 10: FilterBar component

**Files:**
- Create: `frontend/src/components/ui/filter-bar.tsx`

**Step 1: Create the component**

```tsx
"use client";

import { type ReactNode } from "react";
import { Search, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface FilterOption {
  label: string;
  value: string;
}

interface FilterDropdownProps {
  label: string;
  value: string;
  options: FilterOption[];
  onChange: (value: string) => void;
  className?: string;
}

export function FilterDropdown({ label, value, options, onChange, className }: FilterDropdownProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={cn(
        "h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral appearance-none cursor-pointer",
        className
      )}
    >
      <option value="">{label}</option>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}

interface FilterBarProps {
  searchValue: string;
  onSearchChange: (value: string) => void;
  searchPlaceholder?: string;
  children?: ReactNode;  // FilterDropdown slots
  actions?: ReactNode;   // Right-side actions (sync button, etc.)
  className?: string;
}

export function FilterBar({
  searchValue,
  onSearchChange,
  searchPlaceholder = "Search...",
  children,
  actions,
  className,
}: FilterBarProps) {
  return (
    <div className={cn("flex flex-wrap items-center gap-3 mb-4", className)}>
      {/* Search input */}
      <div className="relative flex-1 min-w-[200px] max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder={searchPlaceholder}
          className="h-9 w-full rounded-lg border border-gray-200 bg-white pl-9 pr-8 text-sm text-gray-700 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
        />
        {searchValue && (
          <button
            onClick={() => onSearchChange("")}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        )}
      </div>

      {/* Filter dropdowns */}
      {children}

      {/* Spacer + actions */}
      {actions && <div className="ml-auto flex items-center gap-2">{actions}</div>}
    </div>
  );
}
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/components/ui/filter-bar.tsx
git commit -m "feat: add FilterBar with search input and dropdown filters"
```

---

### Task 11: DataTable component

**Files:**
- Create: `frontend/src/components/ui/data-table.tsx`

**Step 1: Create the component**

```tsx
"use client";

import { useState, type ReactNode } from "react";
import { ChevronUp, ChevronDown, ChevronsUpDown, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { EmptyState } from "@/components/ui/empty-state";

export interface Column<T> {
  key: string;
  header: string;
  sortable?: boolean;
  className?: string;
  render: (row: T, index: number) => ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T) => string;
  onRowClick?: (row: T) => void;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyAction?: { label: string; onClick: () => void };
  page?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
  loading?: boolean;
  className?: string;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  onRowClick,
  emptyTitle = "No data found",
  emptyDescription,
  emptyAction,
  page,
  totalPages,
  onPageChange,
  loading = false,
  className,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  function handleSort(key: string) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  if (!loading && data.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white">
        <EmptyState title={emptyTitle} description={emptyDescription} action={emptyAction} />
      </div>
    );
  }

  return (
    <div className={cn("rounded-lg border border-gray-200 bg-white overflow-hidden", className)}>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50/50">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={cn(
                    "px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider",
                    col.sortable && "cursor-pointer select-none hover:text-gray-700",
                    col.className
                  )}
                  onClick={col.sortable ? () => handleSort(col.key) : undefined}
                >
                  <span className="flex items-center gap-1">
                    {col.header}
                    {col.sortable && (
                      sortKey === col.key ? (
                        sortDir === "asc" ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />
                      ) : (
                        <ChevronsUpDown className="h-3.5 w-3.5 text-gray-300" />
                      )
                    )}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading
              ? Array.from({ length: 5 }).map((_, i) => (
                  <tr key={`skeleton-${i}`}>
                    {columns.map((col) => (
                      <td key={col.key} className="px-4 py-3">
                        <div className="h-4 w-24 rounded bg-gray-100 animate-pulse" />
                      </td>
                    ))}
                  </tr>
                ))
              : data.map((row, idx) => (
                  <tr
                    key={keyExtractor(row)}
                    onClick={onRowClick ? () => onRowClick(row) : undefined}
                    className={cn(
                      "transition-colors",
                      onRowClick && "cursor-pointer hover:bg-gray-50"
                    )}
                  >
                    {columns.map((col) => (
                      <td key={col.key} className={cn("px-4 py-3 text-gray-700", col.className)}>
                        {col.render(row, idx)}
                      </td>
                    ))}
                  </tr>
                ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {page !== undefined && totalPages !== undefined && totalPages > 1 && onPageChange && (
        <div className="flex items-center justify-between border-t border-gray-100 px-4 py-3">
          <p className="text-xs text-gray-500">
            Page {page} of {totalPages}
          </p>
          <div className="flex items-center gap-1">
            <button
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/components/ui/data-table.tsx
git commit -m "feat: add DataTable component with sorting, pagination, loading, and empty states"
```

---

### Task 12: ChartCard component

**Files:**
- Create: `frontend/src/components/ui/chart-card.tsx`

**Step 1: Create the component**

```tsx
"use client";

import { useState, type ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

type TimeRange = "7d" | "30d" | "90d" | "12m";

interface ChartCardProps {
  title: string;
  children: ReactNode;  // The actual Recharts chart
  timeRanges?: TimeRange[];
  defaultRange?: TimeRange;
  onRangeChange?: (range: TimeRange) => void;
  loading?: boolean;
  className?: string;
}

const RANGE_LABELS: Record<TimeRange, string> = {
  "7d": "7D",
  "30d": "30D",
  "90d": "90D",
  "12m": "12M",
};

export function ChartCard({
  title,
  children,
  timeRanges = ["7d", "30d", "90d"],
  defaultRange = "30d",
  onRangeChange,
  loading = false,
  className,
}: ChartCardProps) {
  const [range, setRange] = useState<TimeRange>(defaultRange);

  function handleRange(r: TimeRange) {
    setRange(r);
    onRangeChange?.(r);
  }

  return (
    <div
      className={cn(
        "rounded-xl border border-gray-100 bg-white p-5 shadow-[var(--shadow-card)]",
        className
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
        <div className="flex items-center gap-1 rounded-lg bg-gray-100 p-0.5">
          {timeRanges.map((r) => (
            <button
              key={r}
              onClick={() => handleRange(r)}
              className={cn(
                "rounded-md px-2.5 py-1 text-xs font-medium transition-all duration-[var(--duration-fast)]",
                range === r
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              )}
            >
              {RANGE_LABELS[r]}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <Skeleton className="h-48 w-full rounded-lg" />
      ) : (
        <div className="h-48">{children}</div>
      )}
    </div>
  );
}
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/components/ui/chart-card.tsx
git commit -m "feat: add ChartCard wrapper with time range selector"
```

---

### Task 13: InsightPanel component

**Files:**
- Create: `frontend/src/components/ui/insight-panel.tsx`

**Step 1: Create the component**

```tsx
"use client";

import { useState, type ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Lightbulb, ChevronRight, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface InsightPanelProps {
  children: ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

export function InsightPanel({ children, defaultOpen = false, className }: InsightPanelProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <>
      {/* Toggle button (visible when panel is closed) */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed right-0 top-1/2 -translate-y-1/2 z-40 flex items-center gap-1 rounded-l-lg border border-r-0 border-gray-200 bg-white px-2 py-3 shadow-[var(--shadow-card)] text-gray-500 hover:text-coral transition-colors"
        >
          <Lightbulb className="h-4 w-4" />
          <ChevronRight className="h-3 w-3 rotate-180" />
        </button>
      )}

      {/* Panel */}
      <AnimatePresence>
        {open && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 320, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className={cn(
              "hidden lg:block flex-shrink-0 border-l border-gray-100 bg-white overflow-hidden",
              className
            )}
          >
            <div className="w-[320px] h-full overflow-y-auto">
              <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
                <div className="flex items-center gap-2">
                  <Lightbulb className="h-4 w-4 text-coral" />
                  <h3 className="text-sm font-semibold text-gray-900">Insights</h3>
                </div>
                <button
                  onClick={() => setOpen(false)}
                  className="flex h-7 w-7 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
              <div className="p-5 space-y-4">
                {children}
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}

interface InsightItemProps {
  icon?: ReactNode;
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
  variant?: "default" | "success" | "warning" | "danger";
}

const VARIANT_BORDER: Record<string, string> = {
  default: "border-gray-100",
  success: "border-success/20",
  warning: "border-warning/20",
  danger: "border-danger/20",
};

export function InsightItem({ icon, title, description, action, variant = "default" }: InsightItemProps) {
  return (
    <div className={cn("rounded-lg border p-3", VARIANT_BORDER[variant])}>
      <div className="flex items-start gap-2.5">
        {icon && <span className="mt-0.5 flex-shrink-0">{icon}</span>}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900">{title}</p>
          <p className="text-xs text-gray-500 mt-0.5">{description}</p>
          {action && (
            <button
              onClick={action.onClick}
              className="text-xs font-medium text-coral hover:text-coral-dark mt-2 transition-colors"
            >
              {action.label} →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/components/ui/insight-panel.tsx
git commit -m "feat: add InsightPanel collapsible sidebar with InsightItem cards"
```

---

### Task 14: PageShell component (3-zone layout enforcer)

**Files:**
- Create: `frontend/src/components/ui/page-shell.tsx`

**Step 1: Create the component**

```tsx
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface PageShellProps {
  /** MetricBar or header content above the main area */
  header?: ReactNode;
  /** Main content (DataTable, Grid, Form, etc.) */
  children: ReactNode;
  /** InsightPanel or right sidebar content */
  aside?: ReactNode;
  className?: string;
}

export function PageShell({ header, children, aside, className }: PageShellProps) {
  return (
    <div className={cn("max-w-full", className)}>
      {/* Zone 1: Metrics */}
      {header && <div className="mb-6">{header}</div>}

      {/* Zone 2 + 3: Main + Insight Panel */}
      <div className="flex gap-0">
        {/* Zone 2: Main content */}
        <div className="flex-1 min-w-0">{children}</div>

        {/* Zone 3: Insight panel */}
        {aside}
      </div>
    </div>
  );
}
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/components/ui/page-shell.tsx
git commit -m "feat: add PageShell 3-zone layout component"
```

---

### Task 15: CreativeCard component

**Files:**
- Create: `frontend/src/components/ui/creative-card.tsx`

**Step 1: Create the component**

```tsx
"use client";

import { Play, Image, LayoutGrid } from "lucide-react";
import { cn } from "@/lib/utils";

type CreativeFormat = "video" | "image" | "carousel";

const FORMAT_CONFIG: Record<CreativeFormat, { icon: typeof Play; label: string; color: string }> = {
  video: { icon: Play, label: "Video", color: "bg-coral/80 text-white" },
  image: { icon: Image, label: "Image", color: "bg-purple/80 text-white" },
  carousel: { icon: LayoutGrid, label: "Carousel", color: "bg-cyan/80 text-white" },
};

interface CreativeMetric {
  label: string;
  value: string;
}

interface CreativeCardProps {
  title: string;
  thumbnailUrl?: string;
  format: CreativeFormat;
  metrics?: CreativeMetric[];
  onClick?: () => void;
  className?: string;
}

export function CreativeCard({
  title,
  thumbnailUrl,
  format,
  metrics = [],
  onClick,
  className,
}: CreativeCardProps) {
  const config = FORMAT_CONFIG[format];
  const FormatIcon = config.icon;

  return (
    <div
      onClick={onClick}
      className={cn(
        "group rounded-xl border border-gray-100 bg-white overflow-hidden shadow-[var(--shadow-card)] transition-all duration-[var(--duration-fast)] hover:shadow-[var(--shadow-panel)]",
        onClick && "cursor-pointer",
        className
      )}
    >
      {/* Thumbnail */}
      <div className="relative aspect-[9/16] max-h-48 bg-gray-100 overflow-hidden">
        {thumbnailUrl ? (
          <img src={thumbnailUrl} alt={title} className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <FormatIcon className="h-8 w-8 text-gray-300" />
          </div>
        )}

        {/* Format badge */}
        <span
          className={cn(
            "absolute top-2 left-2 inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-[10px] font-semibold",
            config.color
          )}
        >
          <FormatIcon className="h-3 w-3" />
          {config.label}
        </span>

        {/* Hover overlay with play button for videos */}
        {format === "video" && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/0 group-hover:bg-black/20 transition-colors">
            <div className="h-10 w-10 flex items-center justify-center rounded-full bg-white/90 opacity-0 group-hover:opacity-100 transition-opacity shadow-lg">
              <Play className="h-4 w-4 text-gray-900 ml-0.5" />
            </div>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-3">
        <h4 className="text-sm font-medium text-gray-900 truncate mb-2">{title}</h4>
        {metrics.length > 0 && (
          <div className="flex flex-wrap gap-x-4 gap-y-1">
            {metrics.map((m) => (
              <div key={m.label} className="text-center">
                <p className="text-xs font-semibold text-gray-900 tabular-nums">{m.value}</p>
                <p className="text-[10px] text-gray-400">{m.label}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/components/ui/creative-card.tsx
git commit -m "feat: add CreativeCard with format badge, thumbnail, and metrics overlay"
```

---

### Task 16: Component library barrel export

**Files:**
- Create: `frontend/src/components/ui/index.ts`

**Step 1: Create barrel export**

```tsx
export { Badge } from "./badge";
export { Button } from "./button";
export { Skeleton, SkeletonCard, SkeletonRow } from "./skeleton";
export { Tabs, TabsList, TabsTrigger, TabsContent } from "./tabs";
export { StatusBadge, type StatusVariant } from "./status-badge";
export { MetricCard } from "./metric-card";
export { MetricBar } from "./metric-bar";
export { ActionMenu } from "./action-menu";
export { EmptyState } from "./empty-state";
export { ToastContainer } from "./toast";
export { Modal } from "./modal";
export { FilterBar, FilterDropdown } from "./filter-bar";
export { DataTable, type Column } from "./data-table";
export { ChartCard } from "./chart-card";
export { InsightPanel, InsightItem } from "./insight-panel";
export { PageShell } from "./page-shell";
export { CreativeCard } from "./creative-card";
```

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/components/ui/index.ts
git commit -m "feat: add component library barrel export"
```

---

## Phase 3: Creative Hub Module

### Task 17: Add Creative Hub to navigation

**Files:**
- Modify: `frontend/src/config/navigation.ts`

**Step 1: Add Creative Hub nav item**

Add `Palette` to the lucide-react imports. Add a new nav item after "Content" in the Modules group:

```typescript
{ href: "/creatives", label: "Creative Hub", icon: Palette, group: "Modules" },
```

**Step 2: Commit**

```bash
git add frontend/src/config/navigation.ts
git commit -m "feat: add Creative Hub to sidebar navigation"
```

---

### Task 18: Creative Hub layout + Library page

**Files:**
- Create: `frontend/src/app/(dashboard)/creatives/layout.tsx`
- Create: `frontend/src/app/(dashboard)/creatives/page.tsx`

**Step 1: Create layout with tabs (Library, Performance, Generate)**

Follow the exact pattern from `frontend/src/app/(dashboard)/ads/layout.tsx`. Three tabs:
- Library (default, href `/creatives`)
- Performance (href `/creatives/performance`)
- Generate (href `/creatives/generate`)

Use `PageHeader` with title "Creative Hub" and description "Your unified creative library and performance command center."

**Step 2: Create Library page**

The Library page uses:
- `PageShell` for 3-zone layout
- `MetricBar` with 4 `MetricCard`s: Total Creatives, Avg CTR, Top ROAS, Fatigued (using mock data)
- `FilterBar` with search + format filter (Video/Image/Carousel/All) + sort dropdown (Best CTR/Most Views/Newest)
- A toggle between grid view and table view (default: grid)
- Grid: uses `CreativeCard` components in a responsive grid (`grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4`)
- Table: uses `DataTable` with columns: Thumbnail (small), Title, Format, CTR, Views, ROAS, Campaign, Date
- `InsightPanel` with `InsightItem`s: "Top performer", "Fatigue alert", "Best format"
- Mock data: 12 creative assets with varied formats, metrics, and titles

**Step 3: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 4: Commit**

```bash
git add frontend/src/app/\(dashboard\)/creatives/
git commit -m "feat: add Creative Hub layout and Library page with grid/table views"
```

---

### Task 19: Creative Hub Performance page

**Files:**
- Create: `frontend/src/app/(dashboard)/creatives/performance/page.tsx`

**Step 1: Create Performance page**

Uses:
- `PageShell` for 3-zone layout
- `MetricBar`: Avg CTR, Avg ROAS, Avg Engagement Rate, Fatigue Rate
- Two `ChartCard`s side-by-side:
  - "Performance by Format" — bar chart comparing Video vs Image vs Carousel (CTR, ROAS, Engagement)
  - "Creative Fatigue Timeline" — line chart showing fatigue score over time
- `DataTable` below: "Creative Performance Ranking" — columns: Rank, Title, Format badge, CTR, ROAS, Spend, Views, Fatigue Score
- `InsightPanel`: "Best performing format", "Creatives needing refresh", "A/B test opportunities"
- All mock data

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/app/\(dashboard\)/creatives/performance/page.tsx
git commit -m "feat: add Creative Hub Performance page with charts and rankings"
```

---

### Task 20: Creative Hub Generate page (Symphony AI)

**Files:**
- Create: `frontend/src/app/(dashboard)/creatives/generate/page.tsx`

**Step 1: Create Generate page**

Uses:
- `PageShell` for layout
- `MetricBar`: Creatives Generated, Text Suggestions, Smart Fixes, CTA Recommendations
- Three workflow cards (same pattern as intelligence overview quick links):
  - "Smart Creative" — Generate AI-powered creative assets. Coral gradient. Click → shows form in modal.
  - "Smart Text" — Get AI text recommendations for ad copy. Purple gradient. Click → shows form in modal.
  - "Smart Fix" — Auto-detect and fix creative issues. Cyan gradient. Click → shows form in modal.
- Below workflow cards: "Recent Generations" `DataTable` with columns: Type badge, Prompt/Input, Status, Created At, Actions
- `InsightPanel`: "AI confidence scores", "Trending creative styles", "Best practices"
- All mock data

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/app/\(dashboard\)/creatives/generate/page.tsx
git commit -m "feat: add Creative Hub Generate page with Symphony AI workflows"
```

---

## Phase 4: Advertising Module Redesign

### Task 21: Redesign Campaigns list page

**Files:**
- Modify: `frontend/src/app/(dashboard)/ads/page.tsx`

**Step 1: Rewrite campaigns page using new components**

Replace the entire page with:
- `PageShell` for 3-zone layout
- `MetricBar` with 4 `MetricCard`s: Total Spend ($12.4K, ▲8.2%), ROAS (3.2x, ▲5.1%), Active Campaigns (12), CPA ($4.82, ▼12.3%)
- `FilterBar` with search, status filter (Active/Paused/All), objective filter, account filter, and sync button as action
- `DataTable` with columns: Campaign name (bold, linked), Status (`StatusBadge`), Objective, Budget (with bar visualization), Spend, ROAS, Conversions, CTR, Actions (`ActionMenu` with Edit/Pause/Duplicate)
- `InsightPanel` with insights: top performer, budget pacing alert, underperforming campaign alert
- Replace `alert()` call in sync handler with `toast.success()` / `toast.error()`
- Keep existing API integration (`listCampaigns`, `syncCampaigns`, etc.)

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/app/\(dashboard\)/ads/page.tsx
git commit -m "feat: redesign Campaigns page with Performance Cockpit layout"
```

---

### Task 22: Redesign remaining Ads sub-pages

**Files:**
- Modify: `frontend/src/app/(dashboard)/ads/campaigns/[id]/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/ad-groups/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/ad-groups/[id]/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/creatives/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/reports/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/audiences/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/search/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/split-tests/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/leads/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/identities/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/symphony/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/automation/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/events/page.tsx`
- Modify: `frontend/src/app/(dashboard)/ads/comments/page.tsx`

**Step 1: Apply 3-zone layout to each page**

For each page:
- Wrap in `PageShell`
- Add contextual `MetricBar` with 3-4 `MetricCard`s (use mock trend data)
- Replace hand-coded tables with `DataTable` component
- Replace hand-coded filters with `FilterBar` + `FilterDropdown`
- Replace hand-coded status labels with `StatusBadge`
- Add `InsightPanel` with 2-3 contextual `InsightItem`s
- Replace any `alert()` calls with `toast.success()` / `toast.error()`

**Special cases:**
- `ads/creatives/page.tsx`: Becomes a context-filtered view — add "View all in Creative Hub" link at top, reuse `CreativeCard` grid
- `ads/symphony/page.tsx`: Add "Open in Creative Hub" link, keep as lightweight page with redirect option
- `ads/reports/page.tsx`: Use `ChartCard` for chart wrappers
- Campaign detail (`[id]/page.tsx`): Add `ChartCard` for performance over time chart

**Step 2: Verify build after each batch of 3-4 pages**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit after each batch**

```bash
git commit -m "feat: redesign Ads sub-pages with Performance Cockpit components"
```

---

## Phase 5: Overview, Content, Commerce Redesign

### Task 23: Redesign Overview (Dashboard home)

**Files:**
- Modify: `frontend/src/app/(dashboard)/overview/page.tsx`

**Step 1: Rewrite as command center**

- `PageShell` layout
- `MetricBar` with 5 cross-module `MetricCard`s: Revenue, Ad Spend, ROAS, Content Views, Followers (all with trends and sparklines)
- **Action Items section**: Cards showing items needing attention ("3 campaigns need attention", "5 pending orders", "2 creatives fatigued"). Each card links to relevant module.
- **Module Health Grid**: 6 cards (Commerce, Ads, Content, Creators, Messaging, Intelligence) — each shows a health indicator (green/yellow/red), key metric, and link
- **Recent Activity Feed**: Timeline of recent events with icons and timestamps
- `InsightPanel`: Today's recommendations, trending alerts, quick shortcuts to common actions

**Step 2: Verify build**

Run: `cd frontend && npx next build 2>&1 | tail -5`

**Step 3: Commit**

```bash
git add frontend/src/app/\(dashboard\)/overview/page.tsx
git commit -m "feat: redesign Overview as unified command center"
```

---

### Task 24: Redesign Content module pages

**Files:**
- Modify: `frontend/src/app/(dashboard)/content/page.tsx`
- Modify: `frontend/src/app/(dashboard)/content/videos/page.tsx` (if exists)
- Modify: `frontend/src/app/(dashboard)/content/publish/page.tsx`
- Modify: `frontend/src/app/(dashboard)/content/calendar/page.tsx`

**Step 1: Apply 3-zone layout**

- Videos page: Grid-first using `CreativeCard`, with "View all in Creative Hub" link. `MetricBar` with Views, Engagement Rate, Followers, Publishing Rate.
- Publish page: Add "Open in Creative Hub" link. Keep current form but wrap in `PageShell`.
- Calendar page: Wrap in `PageShell`, add `MetricBar` with scheduled/published counts.

**Step 2: Verify build and commit**

```bash
git commit -m "feat: redesign Content module with Performance Cockpit layout"
```

---

### Task 25: Redesign Commerce module pages

**Files:**
- Modify: `frontend/src/app/(dashboard)/commerce/page.tsx`
- Modify: `frontend/src/app/(dashboard)/commerce/orders/page.tsx`
- Modify: `frontend/src/app/(dashboard)/commerce/products/page.tsx`
- Modify: `frontend/src/app/(dashboard)/commerce/finance/page.tsx`
- Modify: other commerce sub-pages as needed

**Step 1: Apply 3-zone layout**

- Orders: `MetricBar` (Revenue, Orders, AOV, Refund Rate), `DataTable` with `StatusBadge` for order status, `InsightPanel` with fulfillment insights.
- Products: Grid/table toggle using `CreativeCard`-style product cards vs `DataTable`.
- Finance: `ChartCard`s for revenue, settlements, transactions.
- Replace all `alert()` with `toast`.

**Step 2: Verify build and commit**

```bash
git commit -m "feat: redesign Commerce module with Performance Cockpit layout"
```

---

## Phase 6: Remaining Modules Redesign

### Task 26: Redesign Creators module

**Files:** All pages under `frontend/src/app/(dashboard)/creators/`

Apply pattern: `PageShell` + `MetricBar` + `DataTable`/grid + `InsightPanel`. Discovery page uses visual creator cards. Campaigns use `DataTable` with `StatusBadge`. Spark Ads show performance-linked view.

```bash
git commit -m "feat: redesign Creators module with Performance Cockpit layout"
```

---

### Task 27: Redesign Intelligence module

**Files:** All pages under `frontend/src/app/(dashboard)/intelligence/`

Apply pattern: Trends use `ChartCard`, Competitors use comparison `DataTable`, Research uses query form + results `DataTable`. All wrapped in `PageShell` with `MetricBar` and `InsightPanel`.

```bash
git commit -m "feat: redesign Intelligence module with Performance Cockpit layout"
```

---

### Task 28: Redesign Messaging module

**Files:** All pages under `frontend/src/app/(dashboard)/messaging/`

Apply pattern: Conversations list gets `MetricBar` (response time, active conversations, auto-reply rate). Auto-Messages gets `DataTable` with delivery metrics. Wrap in `PageShell`.

```bash
git commit -m "feat: redesign Messaging module with Performance Cockpit layout"
```

---

### Task 29: Redesign Organic module

**Files:** All pages under `frontend/src/app/(dashboard)/organic/`

Apply pattern: Overview gets brand health `MetricBar`. Mentions gets sentiment-tagged feed with `InsightPanel`. Publish adds "Open in Creative Hub" link.

```bash
git commit -m "feat: redesign Organic module with Performance Cockpit layout"
```

---

### Task 30: Redesign LIVE module

**Files:** All pages under `frontend/src/app/(dashboard)/live/`

Apply pattern: Active streams get real-time `MetricBar`. History uses `DataTable`. Analytics uses `ChartCard`s.

```bash
git commit -m "feat: redesign LIVE module with Performance Cockpit layout"
```

---

### Task 31: Redesign Analytics module

**Files:** All pages under `frontend/src/app/(dashboard)/analytics/`

Apply pattern: Overview becomes executive dashboard with cross-module `ChartCard`s. Reports use `DataTable`. Notifications get `FilterBar` + `DataTable` with bulk actions.

```bash
git commit -m "feat: redesign Analytics module with Performance Cockpit layout"
```

---

## Phase 7: Final Polish

### Task 32: Replace all remaining alert() calls with toast

**Files:** Grep all `*.tsx` files for `alert(` and replace with appropriate `toast.success()`, `toast.error()`, or `toast.info()` calls.

Run: Search for `alert(` in `frontend/src/app/`

Replace each with the appropriate toast variant. Import `toast` from `@/lib/toast-store`.

```bash
git commit -m "refactor: replace all alert() calls with toast notifications"
```

---

### Task 33: Verify full build and visual audit

**Step 1: Full build**

```bash
cd frontend && npx next build
```

Expected: Build succeeds with zero errors.

**Step 2: Visual audit checklist**

Run `npm run dev` and verify:
- [ ] Every module page has MetricBar at top
- [ ] Every table uses DataTable component
- [ ] Every filter uses FilterBar component
- [ ] Status indicators use StatusBadge consistently
- [ ] Empty states show actionable messages
- [ ] Toast notifications appear for success/error actions
- [ ] Creative Hub is accessible from sidebar
- [ ] Creative Hub Library shows grid/table toggle
- [ ] InsightPanel opens/closes smoothly
- [ ] Mobile responsive: sidebar collapses, MetricBar stacks

**Step 3: Final commit**

```bash
git commit -m "chore: verify full build and visual audit pass"
```
