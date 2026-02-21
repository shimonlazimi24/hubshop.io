"use client";

import { useState, type ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

type TimeRange = "7d" | "30d" | "90d" | "12m";

interface ChartCardProps {
  title: string;
  children: ReactNode;
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
