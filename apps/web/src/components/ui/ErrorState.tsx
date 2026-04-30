import { AlertTriangle } from "lucide-react";
import { Button } from "./Button";
import { cn } from "@/lib/utils";

export function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
  className,
}: {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-xl border border-red-500/30 bg-red-950/20 px-6 py-12 text-center",
        className,
      )}
      role="alert"
    >
      <AlertTriangle className="h-10 w-10 text-red-400/90" />
      <p className="text-base font-medium text-red-200">{title}</p>
      <p className="max-w-md text-sm text-red-300/90">{message}</p>
      {onRetry ? (
        <Button type="button" variant="secondary" onClick={onRetry}>
          Try again
        </Button>
      ) : null}
    </div>
  );
}
