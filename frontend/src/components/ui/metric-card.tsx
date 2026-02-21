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
    value: number;
    direction: "up" | "down" | "flat";
    label?: string;
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
