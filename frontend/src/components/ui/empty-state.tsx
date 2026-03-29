"use client";

import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import {
	BarChart3,
	Film,
	Inbox,
	Link2,
	Megaphone,
	Package,
	Play,
	Plug,
	Search,
	ShoppingBag,
	Star,
	Target,
	TrendingUp,
	Users,
} from "lucide-react";
import type { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type EmptyStateVariant =
	| "commerce"
	| "advertising"
	| "content"
	| "creators"
	| "analytics"
	| "connect"
	| "generic";

interface VariantConfig {
	primary: LucideIcon;
	secondary: LucideIcon;
	accentColor: string;
	bgGlow: string;
}

const VARIANT_MAP: Record<EmptyStateVariant, VariantConfig> = {
	commerce: {
		primary: ShoppingBag,
		secondary: Package,
		accentColor: "text-coral",
		bgGlow: "from-coral/10 to-coral/5",
	},
	advertising: {
		primary: Megaphone,
		secondary: Target,
		accentColor: "text-purple",
		bgGlow: "from-purple/10 to-purple/5",
	},
	content: {
		primary: Play,
		secondary: Film,
		accentColor: "text-cyan",
		bgGlow: "from-cyan/10 to-cyan/5",
	},
	creators: {
		primary: Users,
		secondary: Star,
		accentColor: "text-info",
		bgGlow: "from-info/10 to-info/5",
	},
	analytics: {
		primary: BarChart3,
		secondary: TrendingUp,
		accentColor: "text-success",
		bgGlow: "from-success/10 to-success/5",
	},
	connect: {
		primary: Link2,
		secondary: Plug,
		accentColor: "text-warning",
		bgGlow: "from-warning/10 to-warning/5",
	},
	generic: {
		primary: Inbox,
		secondary: Search,
		accentColor: "text-foreground-secondary",
		bgGlow: "from-gray-200/40 to-gray-100/20",
	},
};

interface EmptyStateAction {
	label: string;
	onClick: () => void;
}

interface EmptyStateProps {
	variant?: EmptyStateVariant;
	icon?: LucideIcon;
	title: string;
	description?: string;
	action?: EmptyStateAction;
	secondaryAction?: EmptyStateAction;
	children?: ReactNode;
	className?: string;
	compact?: boolean;
}

const iconContainer = {
	hidden: { opacity: 0 },
	visible: {
		opacity: 1,
		transition: { staggerChildren: 0.12, delayChildren: 0.1 },
	},
};

const floatIn = {
	hidden: { opacity: 0, y: 16, scale: 0.85 },
	visible: {
		opacity: 1,
		y: 0,
		scale: 1,
		transition: { type: "spring" as const, stiffness: 260, damping: 20 },
	},
};

const fadeUp = {
	hidden: { opacity: 0, y: 12 },
	visible: {
		opacity: 1,
		y: 0,
		transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] as const },
	},
};

export function EmptyState({
	variant = "generic",
	icon,
	title,
	description,
	action,
	secondaryAction,
	children,
	className,
	compact = false,
}: EmptyStateProps) {
	const config = VARIANT_MAP[variant];
	const PrimaryIcon = icon ?? config.primary;
	const SecondaryIcon = config.secondary;

	return (
		<motion.div
			initial="hidden"
			animate="visible"
			variants={iconContainer}
			className={cn(
				"relative flex flex-col items-center justify-center text-center overflow-hidden",
				compact ? "py-10 px-4" : "py-16 px-6",
				className,
			)}
		>
			{/* Subtle dot pattern background */}
			<div
				className="pointer-events-none absolute inset-0 opacity-[0.35] dark:opacity-[0.15]"
				style={{
					backgroundImage:
						"radial-gradient(circle, currentColor 0.5px, transparent 0.5px)",
					backgroundSize: "16px 16px",
					color: "var(--border)",
				}}
			/>

			{/* Radial glow behind icons */}
			<div
				className={cn(
					"pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-48 w-48 rounded-full bg-gradient-radial blur-2xl",
					config.bgGlow,
				)}
				style={{
					background: `radial-gradient(circle, var(--surface-alt) 0%, transparent 70%)`,
				}}
			/>

			{/* Icon composition */}
			<div className="relative mb-6">
				<motion.div
					variants={floatIn}
					className={cn(
						"flex h-16 w-16 items-center justify-center rounded-2xl border border-border/60 bg-background shadow-[var(--shadow-card)]",
						"dark:bg-surface",
					)}
				>
					<PrimaryIcon className={cn("h-7 w-7", config.accentColor)} />
				</motion.div>

				{/* Secondary icon offset */}
				{!icon && (
					<motion.div
						variants={floatIn}
						className={cn(
							"absolute -bottom-2 -right-3 flex h-9 w-9 items-center justify-center rounded-xl border border-border/60 bg-background shadow-[var(--shadow-card)]",
							"dark:bg-surface",
						)}
					>
						<SecondaryIcon
							className={cn("h-4 w-4", config.accentColor, "opacity-60")}
						/>
					</motion.div>
				)}
			</div>

			{/* Title */}
			<motion.h3
				variants={fadeUp}
				className="relative text-sm font-semibold text-foreground mb-1"
			>
				{title}
			</motion.h3>

			{/* Description */}
			{description && (
				<motion.p
					variants={fadeUp}
					className="relative text-sm text-foreground-secondary max-w-sm mb-5"
				>
					{description}
				</motion.p>
			)}

			{/* Actions */}
			{(action || secondaryAction) && (
				<motion.div
					variants={fadeUp}
					className="relative flex items-center gap-3"
				>
					{action && (
						<Button variant="gradient" size="sm" onClick={action.onClick}>
							{action.label}
						</Button>
					)}
					{secondaryAction && (
						<button
							onClick={secondaryAction.onClick}
							className="text-sm font-medium text-foreground-secondary hover:text-foreground transition-colors"
						>
							{secondaryAction.label}
						</button>
					)}
				</motion.div>
			)}

			{/* Custom children slot */}
			{children && (
				<motion.div variants={fadeUp} className="relative mt-4">
					{children}
				</motion.div>
			)}
		</motion.div>
	);
}
