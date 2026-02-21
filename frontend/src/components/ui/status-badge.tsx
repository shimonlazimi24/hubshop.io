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
