"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
	ArrowRight,
	Megaphone,
	Package,
	RefreshCw,
	RotateCcw,
	Search,
	TrendingUp,
	Zap,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ALL_NAV_ITEMS } from "@/config/navigation";
import { cn } from "@/lib/utils";

interface CommandItem {
	id: string;
	label: string;
	description?: string;
	icon: React.ElementType;
	group: "Pages" | "Commerce" | "Actions";
	action: () => void;
}

interface CommandPaletteProps {
	open: boolean;
	onClose: () => void;
}

const overlayVariants = {
	hidden: { opacity: 0 },
	visible: { opacity: 1 },
};

const panelVariants = {
	hidden: { opacity: 0, scale: 0.92, y: -24 },
	visible: {
		opacity: 1,
		scale: 1,
		y: 0,
		transition: {
			type: "spring" as const,
			damping: 28,
			stiffness: 380,
			mass: 0.8,
		},
	},
	exit: {
		opacity: 0,
		scale: 0.95,
		y: -12,
		transition: { duration: 0.12, ease: "easeIn" as const },
	},
};

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
	const router = useRouter();
	const inputRef = useRef<HTMLInputElement>(null);
	const [query, setQuery] = useState("");
	const [selectedIndex, setSelectedIndex] = useState(0);

	const navigate = useCallback(
		(path: string) => {
			router.push(path);
			onClose();
		},
		[router, onClose],
	);

	const items: CommandItem[] = useMemo(
		() => [
			// Generate from shared nav config
			...ALL_NAV_ITEMS.map((item) => ({
				id: item.href.replace(/\//g, "-").slice(1) || "home",
				label: item.label,
				icon: item.icon,
				group: "Pages" as const,
				action: () => navigate(item.href),
			})),
			// Commerce sub-pages
			{
				id: "orders",
				label: "Orders",
				description: "Commerce > Orders",
				icon: Package,
				group: "Commerce" as const,
				action: () => navigate("/commerce"),
			},
			{
				id: "products",
				label: "Products",
				description: "Commerce > Products",
				icon: Package,
				group: "Commerce" as const,
				action: () => navigate("/commerce/products"),
			},
			{
				id: "returns",
				label: "Returns",
				description: "Commerce > Returns",
				icon: RotateCcw,
				group: "Commerce" as const,
				action: () => navigate("/commerce/returns"),
			},
			{
				id: "commerce-analytics",
				label: "Commerce Analytics",
				description: "Commerce > Analytics",
				icon: TrendingUp,
				group: "Commerce" as const,
				action: () => navigate("/commerce/analytics"),
			},
			// Quick actions
			{
				id: "sync-products",
				label: "Sync Products",
				description: "Pull latest products from TikTok Shop",
				icon: RefreshCw,
				group: "Actions" as const,
				action: () => navigate("/commerce/products"),
			},
			{
				id: "sync-orders",
				label: "Sync Orders",
				description: "Pull latest orders from TikTok Shop",
				icon: RefreshCw,
				group: "Actions" as const,
				action: () => navigate("/commerce"),
			},
			{
				id: "create-campaign",
				label: "Create Campaign",
				description: "Launch a new advertising campaign",
				icon: Megaphone,
				group: "Actions" as const,
				action: () => navigate("/ads/campaigns/create"),
			},
			{
				id: "sync-data",
				label: "Sync All Data",
				description: "Trigger a full platform data sync",
				icon: Zap,
				group: "Actions" as const,
				action: () => navigate("/settings"),
			},
		],
		[navigate],
	);

	const filtered = useMemo(() => {
		if (!query.trim()) return items;
		const q = query.toLowerCase();
		return items.filter(
			(item) =>
				item.label.toLowerCase().includes(q) ||
				item.description?.toLowerCase().includes(q) ||
				item.group.toLowerCase().includes(q),
		);
	}, [items, query]);

	const grouped = useMemo(() => {
		const groups: Record<string, CommandItem[]> = {};
		for (const item of filtered) {
			if (!groups[item.group]) groups[item.group] = [];
			groups[item.group].push(item);
		}
		return groups;
	}, [filtered]);

	// Reset state when opened
	useEffect(() => {
		if (open) {
			setQuery("");
			setSelectedIndex(0);
			setTimeout(() => inputRef.current?.focus(), 50);
		}
	}, [open]);

	// Keyboard navigation
	useEffect(() => {
		if (!open) return;

		function handleKeyDown(e: KeyboardEvent) {
			if (e.key === "ArrowDown") {
				e.preventDefault();
				setSelectedIndex((i) => Math.min(i + 1, filtered.length - 1));
			} else if (e.key === "ArrowUp") {
				e.preventDefault();
				setSelectedIndex((i) => Math.max(i - 1, 0));
			} else if (e.key === "Enter" && filtered[selectedIndex]) {
				e.preventDefault();
				filtered[selectedIndex].action();
			} else if (e.key === "Escape") {
				onClose();
			}
		}

		window.addEventListener("keydown", handleKeyDown);
		return () => window.removeEventListener("keydown", handleKeyDown);
	}, [open, filtered, selectedIndex, onClose]);

	// Reset selected when query changes
	// biome-ignore lint/correctness/useExhaustiveDependencies: intentional reset on query change
	useEffect(() => {
		setSelectedIndex(0);
	}, [query]);

	const flatItems = useMemo(() => {
		const result: Array<{
			item: CommandItem;
			groupLabel: string;
			flatIndex: number;
		}> = [];
		let index = 0;
		for (const [group, groupItems] of Object.entries(grouped)) {
			for (const item of groupItems) {
				result.push({ item, groupLabel: group, flatIndex: index++ });
			}
		}
		return result;
	}, [grouped]);

	return (
		<AnimatePresence>
			{open && (
				<>
					{/* Backdrop */}
					<motion.div
						variants={overlayVariants}
						initial="hidden"
						animate="visible"
						exit="hidden"
						transition={{ duration: 0.15 }}
						className="fixed inset-0 z-50 bg-black/40 dark:bg-black/60 backdrop-blur-sm"
						onClick={onClose}
					/>

					{/* Panel */}
					<motion.div
						variants={panelVariants}
						initial="hidden"
						animate="visible"
						exit="exit"
						className="fixed left-1/2 top-[20%] z-50 w-full max-w-lg -translate-x-1/2 overflow-hidden rounded-xl border border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 shadow-2xl"
					>
						{/* Search input */}
						<div className="flex items-center gap-3 border-b border-gray-100 dark:border-zinc-800 px-4">
							<Search className="h-4 w-4 text-gray-400 dark:text-zinc-500 shrink-0" />
							<input
								ref={inputRef}
								type="text"
								value={query}
								onChange={(e) => setQuery(e.target.value)}
								placeholder="Search pages, actions..."
								className="flex-1 border-none bg-transparent py-3.5 text-sm text-gray-900 dark:text-zinc-100 placeholder:text-gray-400 dark:placeholder:text-zinc-500 outline-none"
							/>
							<kbd className="rounded border border-gray-200 dark:border-zinc-700 bg-gray-50 dark:bg-zinc-800 px-1.5 py-0.5 text-[10px] font-medium text-gray-400 dark:text-zinc-500">
								ESC
							</kbd>
						</div>

						{/* Results */}
						<div className="max-h-72 overflow-y-auto py-2">
							{filtered.length === 0 ? (
								<div className="px-4 py-8 text-center">
									<p className="text-sm text-gray-400 dark:text-zinc-500">
										No results for &ldquo;{query}&rdquo;
									</p>
								</div>
							) : (
								(() => {
									let lastGroup = "";
									return flatItems.map(
										({ item, groupLabel, flatIndex: idx }) => {
											const showGroupHeader = groupLabel !== lastGroup;
											lastGroup = groupLabel;
											const isSelected = idx === selectedIndex;
											const Icon = item.icon;
											return (
												<div key={item.id}>
													{showGroupHeader && (
														<p className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-400 dark:text-zinc-500">
															{groupLabel}
														</p>
													)}
													<button
														onClick={() => item.action()}
														onMouseEnter={() => setSelectedIndex(idx)}
														className={cn(
															"flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors",
															isSelected
																? "bg-gray-50 dark:bg-zinc-800"
																: "hover:bg-gray-50 dark:hover:bg-zinc-800",
														)}
													>
														<Icon
															className={cn(
																"h-4 w-4 shrink-0",
																isSelected
																	? "text-coral"
																	: "text-gray-400 dark:text-zinc-500",
															)}
														/>
														<div className="min-w-0 flex-1">
															<p
																className={cn(
																	"text-sm",
																	isSelected
																		? "text-gray-900 dark:text-zinc-100 font-medium"
																		: "text-gray-700 dark:text-zinc-300",
																)}
															>
																{item.label}
															</p>
															{item.description && (
																<p className="text-xs text-gray-400 dark:text-zinc-500 truncate">
																	{item.description}
																</p>
															)}
														</div>
														{isSelected && (
															<ArrowRight className="h-3.5 w-3.5 text-gray-300 dark:text-zinc-600" />
														)}
													</button>
												</div>
											);
										},
									);
								})()
							)}
						</div>

						{/* Footer */}
						<div className="flex items-center justify-between border-t border-gray-100 dark:border-zinc-800 px-4 py-2">
							<div className="flex items-center gap-3 text-[10px] text-gray-400 dark:text-zinc-500">
								<span>
									<kbd className="rounded border border-gray-200 dark:border-zinc-700 bg-gray-50 dark:bg-zinc-800 px-1 py-0.5 font-medium">
										&uarr;&darr;
									</kbd>{" "}
									Navigate
								</span>
								<span>
									<kbd className="rounded border border-gray-200 dark:border-zinc-700 bg-gray-50 dark:bg-zinc-800 px-1 py-0.5 font-medium">
										&crarr;
									</kbd>{" "}
									Select
								</span>
								<span>
									<kbd className="rounded border border-gray-200 dark:border-zinc-700 bg-gray-50 dark:bg-zinc-800 px-1 py-0.5 font-medium">
										Esc
									</kbd>{" "}
									Close
								</span>
							</div>
						</div>
					</motion.div>
				</>
			)}
		</AnimatePresence>
	);
}
