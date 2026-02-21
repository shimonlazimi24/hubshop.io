import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface PageShellProps {
  header?: ReactNode;
  children: ReactNode;
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
