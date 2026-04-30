import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function PageHeader({
  title,
  description,
  actions,
  className,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "mb-6 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between",
        className,
      )}
    >
      <div>
        <h1 className="text-xl font-semibold text-gray-900 dark:text-zinc-100 md:text-2xl">
          {title}
        </h1>
        {description ? (
          <p className="mt-0.5 max-w-2xl text-sm text-gray-500 dark:text-zinc-400">
            {description}
          </p>
        ) : null}
      </div>
      {actions ? (
        <div className="mt-2 flex items-center gap-2 sm:mt-0">{actions}</div>
      ) : null}
    </div>
  );
}
