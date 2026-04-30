import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { Minus, TrendingDown, TrendingUp } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

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
  delay?: number;
}

function useAnimatedCounter(target: number, duration = 800): number {
  const [display, setDisplay] = useState(target);
  const rafRef = useRef<number>(0);
  const startRef = useRef<number | null>(null);
  const fromRef = useRef(target);

  useEffect(() => {
    const from = fromRef.current;
    if (from === target) return;

    startRef.current = null;

    const tick = (timestamp: number) => {
      if (startRef.current === null) startRef.current = timestamp;
      const elapsed = timestamp - startRef.current;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - (1 - progress) ** 3;
      const current = from + (target - from) * eased;
      setDisplay(Math.round(current));

      if (progress < 1) {
        rafRef.current = requestAnimationFrame(tick);
      } else {
        fromRef.current = target;
      }
    };

    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, [target, duration]);

  return display;
}

function MiniSparkline({
  data,
  className,
}: {
  data: number[];
  className?: string;
}) {
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

  const areaPoints = data.map((v, i) => ({
    x: i * step,
    y: h - ((v - min) / range) * h,
  }));
  const areaPath = [
    `M ${areaPoints[0].x},${areaPoints[0].y}`,
    ...areaPoints.slice(1).map((p) => `L ${p.x},${p.y}`),
    `L ${w},${h}`,
    `L 0,${h}`,
    "Z",
  ].join(" ");

  const gradientId = `sparkline-gradient-${Math.random().toString(36).slice(2, 8)}`;

  return (
    <svg
      width={w}
      height={h}
      className={cn("text-coral", className)}
      viewBox={`0 0 ${w} ${h}`}
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="currentColor" stopOpacity="0.3" />
          <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill={`url(#${gradientId})`} />
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

function ShimmerBlock({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-lg bg-zinc-800/50",
        className,
      )}
    >
      <div
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.06) 50%, transparent 100%)",
          animation: "shimmer-sweep 1.8s ease-in-out infinite",
        }}
      />
    </div>
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
  delay = 0,
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

  const numericValue = typeof value === "number" ? value : null;
  const animatedValue = useAnimatedCounter(numericValue ?? 0);

  const formatValue = useCallback(() => {
    if (typeof value === "string") return value;
    return animatedValue.toLocaleString();
  }, [value, animatedValue]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.4,
        delay,
        ease: [0.25, 0.46, 0.45, 0.94],
      }}
      className={cn(
        "group relative rounded-xl border border-zinc-800 bg-zinc-900 p-5 transition-all duration-200",
        "shadow-[0_1px_3px_rgba(0,0,0,0.3)]",
        "hover:border-transparent hover:shadow-[0_4px_16px_rgba(0,0,0,0.4)]",
        className,
      )}
    >
      <div
        className="pointer-events-none absolute inset-0 rounded-xl opacity-0 transition-opacity duration-200 group-hover:opacity-100"
        style={{
          padding: "1px",
          background: "linear-gradient(135deg, var(--coral), var(--purple))",
          mask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
          maskComposite: "exclude",
          WebkitMaskComposite: "xor",
          borderRadius: "inherit",
        }}
      />

      <div className="mb-3 flex items-start justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-zinc-400">
          {label}
        </p>
        {Icon && (
          <div
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-800",
              iconColor,
            )}
          >
            <Icon className="h-4 w-4" />
          </div>
        )}
      </div>

      {loading ? (
        <ShimmerBlock className="mb-2 h-8 w-24" />
      ) : (
        <p className="text-2xl font-bold tabular-nums text-white">
          {formatValue()}
        </p>
      )}

      <div className="mt-2 flex items-center justify-between">
        {trend && !loading ? (
          <span
            className={cn(
              "flex items-center gap-1 text-xs font-medium",
              trendColor,
            )}
          >
            <TrendIcon className="h-3 w-3" />
            {trend.direction !== "flat" && (
              <span>
                {trend.direction === "up" ? "+" : ""}
                {trend.value}%
              </span>
            )}
            {trend.label && (
              <span className="ml-1 text-zinc-500">{trend.label}</span>
            )}
          </span>
        ) : (
          <span />
        )}
        {sparklineData && !loading && <MiniSparkline data={sparklineData} />}
      </div>
    </motion.div>
  );
}
