import type { HTMLAttributes } from "react";
import { cn } from "../../lib/cn";

export function Badge({
  className,
  ...props
}: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md border border-zinc-600 bg-zinc-800 px-2 py-0.5 text-xs font-medium text-zinc-300",
        className,
      )}
      {...props}
    />
  );
}
