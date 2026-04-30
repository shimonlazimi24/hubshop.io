import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
}: {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-700 bg-zinc-900/50 px-8 py-14 text-center",
        className,
      )}
    >
      {Icon ? (
        <Icon
          className="mb-4 h-10 w-10 text-zinc-500"
          strokeWidth={1.25}
        />
      ) : null}
      <p className="text-base font-medium text-zinc-100">{title}</p>
      {description ? (
        <p className="mt-2 max-w-md text-sm text-zinc-400">{description}</p>
      ) : null}
      {action ? <div className="mt-6">{action}</div> : null}
    </div>
  );
}
