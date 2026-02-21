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
