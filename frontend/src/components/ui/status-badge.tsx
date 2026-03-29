"use client";

import { cn } from "@/lib/utils";

export type StatusVariant =
	| "active"
	| "paused"
	| "error"
	| "draft"
	| "completed"
	| "syncing"
	| "warning";

export type StatusBadgeSize = "sm" | "md" | "lg";

const VARIANT_STYLES: Record<StatusVariant, string> = {
	active: "bg-success/10 text-success border-success/20",
	completed: "bg-success/10 text-success border-success/20",
	paused: "bg-zinc-800 text-zinc-400 border-zinc-700",
	draft: "bg-zinc-800 text-zinc-500 border-zinc-700",
	error: "bg-danger/10 text-danger border-danger/20",
	syncing: "bg-info/10 text-info border-info/20",
	warning: "bg-warning/10 text-warning border-warning/20",
};

const DOT_STYLES: Record<StatusVariant, string> = {
	active: "bg-success",
	completed: "bg-success",
	paused: "bg-zinc-500",
	draft: "bg-zinc-500",
	error: "bg-danger",
	syncing: "bg-info animate-pulse",
	warning: "bg-warning",
};

const SIZE_STYLES: Record<StatusBadgeSize, string> = {
	sm: "px-1.5 py-px text-[10px] gap-1",
	md: "px-2.5 py-0.5 text-xs gap-1.5",
	lg: "px-3 py-1 text-sm gap-2",
};

const DOT_SIZES: Record<StatusBadgeSize, string> = {
	sm: "h-1 w-1",
	md: "h-1.5 w-1.5",
	lg: "h-2 w-2",
};

interface StatusBadgeProps {
	variant: StatusVariant;
	label?: string;
	size?: StatusBadgeSize;
	className?: string;
}

export function StatusBadge({
	variant,
	label,
	size = "md",
	className,
}: StatusBadgeProps) {
	const displayLabel =
		label ?? variant.charAt(0).toUpperCase() + variant.slice(1);
	const isLive = variant === "active";

	return (
		<span
			className={cn(
				"inline-flex items-center rounded-full border font-medium",
				SIZE_STYLES[size],
				VARIANT_STYLES[variant],
				className,
			)}
		>
			<span
				className={cn(
					"rounded-full",
					DOT_SIZES[size],
					DOT_STYLES[variant],
					isLive && "animate-live-pulse",
				)}
			/>
			{displayLabel}
		</span>
	);
}
