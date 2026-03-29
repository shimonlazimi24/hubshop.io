"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
	Check,
	ChevronDown,
	ChevronUp,
	LayoutDashboard,
	Link2,
	RefreshCw,
	Rocket,
	Sparkles,
	UserPlus,
	X,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { cn } from "@/lib/utils";

const STORAGE_KEY = "frodo_onboarding";

interface ChecklistStep {
	id: string;
	title: string;
	description: string;
	href: string;
	actionLabel: string;
	icon: typeof Rocket;
}

const STEPS: readonly ChecklistStep[] = [
	{
		id: "account",
		title: "Create your account",
		description: "You're already here — nice work!",
		href: "/overview",
		actionLabel: "Done",
		icon: Sparkles,
	},
	{
		id: "connect",
		title: "Connect a TikTok account",
		description:
			"Link your TikTok Shop, Developer, or Marketing account to start syncing data.",
		href: "/connect",
		actionLabel: "Connect now",
		icon: Link2,
	},
	{
		id: "sync",
		title: "Sync your first data",
		description:
			"Once connected, trigger a sync to pull in orders, ads, and content.",
		href: "/connect",
		actionLabel: "Start sync",
		icon: RefreshCw,
	},
	{
		id: "explore",
		title: "Explore your dashboard",
		description:
			"Browse Commerce, Ads, Content, and Analytics to see what Frodo can do.",
		href: "/overview",
		actionLabel: "Take a tour",
		icon: LayoutDashboard,
	},
	{
		id: "invite",
		title: "Invite your team",
		description:
			"Add team members to your workspace so everyone stays in sync.",
		href: "/settings",
		actionLabel: "Invite team",
		icon: UserPlus,
	},
] as const;

interface OnboardingState {
	completed: string[];
	dismissed: boolean;
	collapsed: boolean;
}

function loadState(): OnboardingState {
	if (typeof window === "undefined") {
		return { completed: ["account"], dismissed: false, collapsed: false };
	}
	try {
		const raw = localStorage.getItem(STORAGE_KEY);
		if (raw) {
			const parsed = JSON.parse(raw) as OnboardingState;
			// Account is always complete
			if (!parsed.completed.includes("account")) {
				parsed.completed.push("account");
			}
			return parsed;
		}
	} catch {
		// ignore corrupt storage
	}
	return { completed: ["account"], dismissed: false, collapsed: false };
}

function saveState(state: OnboardingState) {
	try {
		localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
	} catch {
		// ignore quota errors
	}
}

const listContainer = {
	hidden: { opacity: 0 },
	visible: {
		opacity: 1,
		transition: { staggerChildren: 0.06, delayChildren: 0.15 },
	},
};

const listItem = {
	hidden: { opacity: 0, x: -12 },
	visible: {
		opacity: 1,
		x: 0,
		transition: { type: "spring" as const, stiffness: 300, damping: 24 },
	},
};

const checkSpring = {
	initial: { scale: 0, opacity: 0 },
	animate: {
		scale: 1,
		opacity: 1,
		transition: { type: "spring" as const, stiffness: 400, damping: 15 },
	},
};

export function OnboardingChecklist() {
	const [state, setState] = useState<OnboardingState>({
		completed: ["account"],
		dismissed: false,
		collapsed: false,
	});
	const [mounted, setMounted] = useState(false);

	// Load from localStorage after mount
	useEffect(() => {
		setState(loadState());
		setMounted(true);
	}, []);

	const completedCount = state.completed.length;
	const totalSteps = STEPS.length;
	const progressPercent = (completedCount / totalSteps) * 100;

	const toggleComplete = useCallback((stepId: string) => {
		setState((prev) => {
			// "account" cannot be unchecked
			if (stepId === "account") return prev;
			const alreadyDone = prev.completed.includes(stepId);
			const completed = alreadyDone
				? prev.completed.filter((id) => id !== stepId)
				: [...prev.completed, stepId];
			const next = { ...prev, completed };
			saveState(next);
			return next;
		});
	}, []);

	const toggleCollapse = useCallback(() => {
		setState((prev) => {
			const next = { ...prev, collapsed: !prev.collapsed };
			saveState(next);
			return next;
		});
	}, []);

	const dismiss = useCallback(() => {
		setState((prev) => {
			const next = { ...prev, dismissed: true };
			saveState(next);
			return next;
		});
	}, []);

	// Don't render until mounted (avoids hydration mismatch with localStorage)
	if (!mounted) return null;

	// Don't render if dismissed or all steps complete
	if (state.dismissed || completedCount === totalSteps) return null;

	return (
		<motion.div
			initial={{ opacity: 0, y: 16 }}
			animate={{ opacity: 1, y: 0 }}
			exit={{ opacity: 0, y: -8 }}
			transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
			className={cn(
				"relative rounded-2xl border border-border bg-background overflow-hidden",
				"shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-panel)] transition-shadow duration-[var(--duration-normal)]",
				// Subtle gradient border effect
				"before:absolute before:inset-0 before:rounded-2xl before:p-[1px] before:pointer-events-none",
				"before:bg-gradient-to-br before:from-coral/20 before:via-transparent before:to-purple/20",
				"before:-z-10",
			)}
		>
			{/* Glass header */}
			<div className="flex items-center justify-between px-5 py-4 bg-surface/50 backdrop-blur-sm border-b border-border/50">
				<div className="flex items-center gap-3">
					<div className="flex h-8 w-8 items-center justify-center rounded-lg gradient-bg shadow-sm">
						<Rocket className="h-4 w-4 text-white" />
					</div>
					<div>
						<h3 className="text-sm font-semibold text-foreground">
							Getting Started
						</h3>
						<p className="text-xs text-foreground-secondary">
							{completedCount} of {totalSteps} steps complete
						</p>
					</div>
				</div>

				<div className="flex items-center gap-1">
					<button
						onClick={toggleCollapse}
						className="flex h-7 w-7 items-center justify-center rounded-md text-foreground-secondary hover:bg-surface hover:text-foreground transition-colors"
						aria-label={
							state.collapsed ? "Expand checklist" : "Collapse checklist"
						}
					>
						{state.collapsed ? (
							<ChevronDown className="h-4 w-4" />
						) : (
							<ChevronUp className="h-4 w-4" />
						)}
					</button>
					<button
						onClick={dismiss}
						className="flex h-7 w-7 items-center justify-center rounded-md text-foreground-secondary hover:bg-surface hover:text-foreground transition-colors"
						aria-label="Dismiss checklist"
					>
						<X className="h-4 w-4" />
					</button>
				</div>
			</div>

			{/* Progress bar */}
			<div className="h-1 bg-surface">
				<motion.div
					className="h-full gradient-bg rounded-r-full"
					initial={{ width: 0 }}
					animate={{ width: `${progressPercent}%` }}
					transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
				/>
			</div>

			{/* Checklist items */}
			<AnimatePresence initial={false}>
				{!state.collapsed && (
					<motion.div
						initial={{ height: 0, opacity: 0 }}
						animate={{ height: "auto", opacity: 1 }}
						exit={{ height: 0, opacity: 0 }}
						transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
					>
						<motion.ul
							variants={listContainer}
							initial="hidden"
							animate="visible"
							className="divide-y divide-border/50 px-5"
						>
							{STEPS.map((step) => {
								const isComplete = state.completed.includes(step.id);
								const StepIcon = step.icon;
								return (
									<motion.li
										key={step.id}
										variants={listItem}
										className="flex items-start gap-3.5 py-4"
									>
										{/* Checkbox */}
										<button
											onClick={() => toggleComplete(step.id)}
											disabled={step.id === "account"}
											className={cn(
												"flex h-5 w-5 shrink-0 mt-0.5 items-center justify-center rounded-md border-2 transition-all duration-[var(--duration-fast)]",
												isComplete
													? "border-coral bg-coral text-white"
													: "border-border hover:border-coral/50 bg-transparent",
												step.id === "account" && "cursor-default",
											)}
											aria-label={`Mark "${step.title}" as ${isComplete ? "incomplete" : "complete"}`}
										>
											<AnimatePresence mode="wait">
												{isComplete && (
													<motion.div
														key="check"
														initial={checkSpring.initial}
														animate={checkSpring.animate}
													>
														<Check className="h-3 w-3" strokeWidth={3} />
													</motion.div>
												)}
											</AnimatePresence>
										</button>

										{/* Content */}
										<div className="flex-1 min-w-0">
											<p
												className={cn(
													"text-sm font-medium transition-colors",
													isComplete
														? "text-foreground-secondary line-through"
														: "text-foreground",
												)}
											>
												{step.title}
											</p>
											<p className="text-xs text-foreground-secondary mt-0.5">
												{step.description}
											</p>
										</div>

										{/* Action */}
										{!isComplete && (
											<Link
												href={step.href}
												className="flex shrink-0 items-center gap-1.5 rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-medium text-foreground hover:bg-surface-alt hover:border-coral/30 transition-all duration-[var(--duration-fast)]"
											>
												<StepIcon className="h-3 w-3" />
												{step.actionLabel}
											</Link>
										)}
									</motion.li>
								);
							})}
						</motion.ul>
					</motion.div>
				)}
			</AnimatePresence>
		</motion.div>
	);
}
