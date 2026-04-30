import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface TooltipProps {
  content: string;
  side?: "top" | "right" | "bottom" | "left";
  children: ReactNode;
  className?: string;
}

const sideStyles = {
  top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
  right: "left-full top-1/2 -translate-y-1/2 ml-2",
  bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
  left: "right-full top-1/2 -translate-y-1/2 mr-2",
};

export function Tooltip({
  content,
  side = "right",
  children,
  className,
}: TooltipProps) {
  return (
    <div className={cn("group relative", className)}>
      {children}
      <div
        className={cn(
          "pointer-events-none absolute z-50 whitespace-nowrap rounded-md bg-gray-900 px-2.5 py-1.5 text-xs text-white opacity-0 shadow-lg transition-opacity duration-150 group-hover:opacity-100 dark:bg-zinc-800",
          sideStyles[side],
        )}
      >
        {content}
      </div>
    </div>
  );
}
