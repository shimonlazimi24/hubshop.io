import { cn } from "@/lib/utils";

type Tone = "success" | "warning" | "danger" | "neutral" | "info";

const tones: Record<Tone, string> = {
  success:
    "border-emerald-500/40 bg-emerald-950/50 text-emerald-300",
  warning:
    "border-amber-500/40 bg-amber-950/50 text-amber-200",
  danger: "border-red-500/40 bg-red-950/50 text-red-300",
  neutral: "border-zinc-600 bg-zinc-800 text-zinc-300",
  info: "border-cyan-500/40 bg-cyan-950/50 text-cyan-200",
};

export function StatusBadge({
  tone,
  children,
  className,
}: {
  tone: Tone;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium uppercase tracking-wide",
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
