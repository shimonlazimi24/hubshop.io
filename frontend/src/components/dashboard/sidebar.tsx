"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
	Building2,
	ChevronDown,
	ChevronRight,
	ChevronsLeft,
	ChevronsRight,
	LogOut,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMemo, useState } from "react";
import { Tooltip } from "@/components/ui/tooltip";
import { NAV_ITEMS, SETTINGS_ITEM } from "@/config/navigation";
import type { UserResponse } from "@/lib/api";
import { cn } from "@/lib/utils";

const GROUPS = ["Main", "Modules", "Insights"] as const;

/** Keyboard shortcut hints for top nav items (expanded mode only). */
const SHORTCUT_HINTS: Record<string, string> = {
	"/overview": "\u23181",
	"/connect": "\u23182",
};

interface SidebarProps {
	collapsed: boolean;
	onToggle: () => void;
	user: UserResponse | null;
	onLogout: () => void;
}

/** Extract up to two initials from a full name. */
function getInitials(name: string | undefined): string {
	if (!name) return "U";
	const parts = name.trim().split(/\s+/);
	if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
	return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

export function Sidebar({ collapsed, onToggle, user, onLogout }: SidebarProps) {
	const pathname = usePathname();

	// Track which groups are expanded (all open by default).
	const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(
		{
			Main: true,
			Modules: true,
			Insights: true,
		},
	);

	const toggleGroup = (group: string) => {
		setExpandedGroups((prev) => ({ ...prev, [group]: !prev[group] }));
	};

	// Pre-compute grouped items to avoid re-filtering every render.
	const groupedItems = useMemo(
		() =>
			GROUPS.map((group) => ({
				group,
				items: NAV_ITEMS.filter((item) => item.group === group),
			})).filter(({ items }) => items.length > 0),
		[],
	);

	return (
		<motion.aside
			className={cn(
				"hidden md:flex flex-col bg-zinc-950 text-zinc-300 transition-colors",
				"border-r border-zinc-800/60",
			)}
			animate={{ width: collapsed ? 64 : 256 }}
			transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
		>
			{/* ── Logo + Workspace ── */}
			<div
				className={cn(
					"border-b border-zinc-800/60",
					collapsed ? "px-3 py-4" : "p-4",
				)}
			>
				<Link href="/overview" className="flex items-center gap-2.5 group">
					{/* Logo square with shimmer */}
					<div className="relative flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-coral to-purple animate-logo-shimmer glow-gold-always">
						<span className="relative z-10 text-sm font-bold text-white select-none">
							F
						</span>
					</div>

					<AnimatePresence mode="wait">
						{!collapsed && (
							<motion.div
								className="min-w-0"
								initial={{ opacity: 0, x: -8 }}
								animate={{ opacity: 1, x: 0 }}
								exit={{ opacity: 0, x: -8 }}
								transition={{ duration: 0.15 }}
							>
								<h1 className="text-sm font-semibold text-zinc-100 truncate">
									Frodo
								</h1>
								<p className="text-[10px] text-zinc-500 truncate">
									One platform to rule them all
								</p>
							</motion.div>
						)}
					</AnimatePresence>
				</Link>

				{/* Workspace switcher */}
				<AnimatePresence>
					{!collapsed && (
						<motion.button
							initial={{ opacity: 0, height: 0 }}
							animate={{ opacity: 1, height: "auto" }}
							exit={{ opacity: 0, height: 0 }}
							transition={{ duration: 0.15 }}
							className="mt-3 flex w-full items-center gap-2 rounded-lg border border-zinc-800 px-2.5 py-1.5 text-xs text-zinc-400 hover:bg-zinc-900 hover:border-zinc-700 transition-colors overflow-hidden"
							aria-disabled="true"
							title="Workspace switcher coming soon"
						>
							<Building2 className="h-3.5 w-3.5 text-zinc-500" />
							<span className="flex-1 text-left truncate">
								{user?.full_name?.split(" ")[0] ?? "My"}&apos;s Workspace
							</span>
							<ChevronDown className="h-3 w-3 text-zinc-500" />
						</motion.button>
					)}
				</AnimatePresence>
			</div>

			{/* ── Navigation ── */}
			<nav className="flex-1 overflow-y-auto py-3 scrollbar-none">
				{groupedItems.map(({ group, items }) => {
					const isExpanded = expandedGroups[group] ?? true;

					return (
						<div key={group} className="mb-1">
							{/* Group header — collapsible */}
							{!collapsed ? (
								<button
									onClick={() => toggleGroup(group)}
									className="flex w-full items-center gap-1 px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-zinc-500 hover:text-zinc-300 transition-colors"
								>
									<motion.span
										animate={{ rotate: isExpanded ? 90 : 0 }}
										transition={{ duration: 0.15 }}
										className="flex items-center"
									>
										<ChevronRight className="h-3 w-3" />
									</motion.span>
									<span>{group}</span>
								</button>
							) : (
								<div className="mx-auto my-1.5 h-px w-6 bg-zinc-800" />
							)}

							{/* Group items */}
							<AnimatePresence initial={false}>
								{(isExpanded || collapsed) && (
									<motion.div
										initial={collapsed ? false : { height: 0, opacity: 0 }}
										animate={{ height: "auto", opacity: 1 }}
										exit={{ height: 0, opacity: 0 }}
										transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
										className="overflow-hidden"
									>
										<div className="space-y-0.5 px-2">
											{items.map((item) => {
												const isActive =
													pathname === item.href ||
													pathname.startsWith(`${item.href}/`);
												const Icon = item.icon;
												const shortcut = SHORTCUT_HINTS[item.href];

												const link = (
													<Link
														key={item.href}
														href={item.href}
														className={cn(
															"group/item relative flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors duration-150",
															isActive
																? "text-zinc-100"
																: "text-zinc-400 hover:text-zinc-200",
															collapsed && "justify-center px-0",
														)}
													>
														{/* Animated active indicator pill */}
														{isActive && (
															<motion.div
																layoutId="sidebar-active-pill"
																className="absolute inset-0 rounded-lg bg-zinc-800/80 border border-zinc-700/50"
																transition={{
																	type: "spring",
																	stiffness: 350,
																	damping: 30,
																}}
															/>
														)}

														{/* Hover background */}
														{!isActive && (
															<span className="absolute inset-0 rounded-lg bg-zinc-800/0 group-hover/item:bg-zinc-800/50 transition-colors duration-150" />
														)}

														<Icon
															className={cn(
																"relative z-10 h-[18px] w-[18px] shrink-0 transition-colors duration-150",
																isActive
																	? "text-coral"
																	: "text-zinc-500 group-hover/item:text-zinc-300",
															)}
														/>

														{!collapsed && (
															<>
																<span className="relative z-10 truncate">
																	{item.label}
																</span>

																{/* Keyboard shortcut hint */}
																{shortcut && (
																	<span className="relative z-10 ml-auto hidden xl:inline-flex items-center rounded bg-zinc-800 px-1 py-0.5 text-[9px] font-mono text-zinc-500">
																		{shortcut}
																	</span>
																)}

																{/* Badge */}
																{item.badge !== undefined && (
																	<span
																		className={cn(
																			"relative z-10 ml-auto rounded-full bg-coral/15 px-1.5 py-0.5 text-[10px] font-medium text-coral",
																			typeof item.badge === "number" &&
																				item.badge > 0 &&
																				"animate-pulse-badge",
																		)}
																	>
																		{item.badge}
																	</span>
																)}
															</>
														)}
													</Link>
												);

												if (collapsed) {
													return (
														<Tooltip
															key={item.href}
															content={item.label}
															side="right"
														>
															{link}
														</Tooltip>
													);
												}

												return <div key={item.href}>{link}</div>;
											})}
										</div>
									</motion.div>
								)}
							</AnimatePresence>
						</div>
					);
				})}
			</nav>

			{/* ── Bottom Section ── */}
			<div
				className={cn(
					"border-t border-zinc-800/60",
					collapsed ? "px-2 py-3" : "px-2 py-3",
				)}
			>
				{/* Settings link */}
				{collapsed ? (
					<Tooltip content="Settings" side="right">
						<Link
							href={SETTINGS_ITEM.href}
							className={cn(
								"group/item relative flex items-center justify-center rounded-lg py-2 text-sm transition-colors",
								pathname === SETTINGS_ITEM.href
									? "text-coral"
									: "text-zinc-500 hover:text-zinc-300",
							)}
						>
							{pathname === SETTINGS_ITEM.href && (
								<motion.div
									layoutId="sidebar-active-pill"
									className="absolute inset-0 rounded-lg bg-zinc-800/80 border border-zinc-700/50"
									transition={{
										type: "spring",
										stiffness: 350,
										damping: 30,
									}}
								/>
							)}
							<SETTINGS_ITEM.icon className="relative z-10 h-[18px] w-[18px]" />
						</Link>
					</Tooltip>
				) : (
					<Link
						href={SETTINGS_ITEM.href}
						className={cn(
							"group/item relative flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors",
							pathname === SETTINGS_ITEM.href
								? "text-zinc-100"
								: "text-zinc-400 hover:text-zinc-200",
						)}
					>
						{pathname === SETTINGS_ITEM.href && (
							<motion.div
								layoutId="sidebar-active-pill"
								className="absolute inset-0 rounded-lg bg-zinc-800/80 border border-zinc-700/50"
								transition={{
									type: "spring",
									stiffness: 350,
									damping: 30,
								}}
							/>
						)}
						{!pathname.startsWith(SETTINGS_ITEM.href) && (
							<span className="absolute inset-0 rounded-lg bg-zinc-800/0 group-hover/item:bg-zinc-800/50 transition-colors duration-150" />
						)}
						<SETTINGS_ITEM.icon
							className={cn(
								"relative z-10 h-[18px] w-[18px]",
								pathname === SETTINGS_ITEM.href
									? "text-coral"
									: "text-zinc-500",
							)}
						/>
						<span className="relative z-10">Settings</span>
					</Link>
				)}

				{/* User info + sign out */}
				<AnimatePresence>
					{!collapsed && user && (
						<motion.div
							initial={{ opacity: 0, height: 0 }}
							animate={{ opacity: 1, height: "auto" }}
							exit={{ opacity: 0, height: 0 }}
							transition={{ duration: 0.15 }}
							className="mt-2 flex items-center gap-2 rounded-lg px-2.5 py-2 overflow-hidden"
						>
							{/* Avatar with gradient ring */}
							<div className="relative flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-coral via-purple to-gold text-[10px] font-bold text-white glow-coral select-none">
								{getInitials(user.full_name)}
							</div>
							<div className="min-w-0 flex-1">
								<p className="text-xs font-medium text-zinc-200 truncate">
									{user.full_name}
								</p>
								<p className="text-[10px] text-zinc-500 truncate">
									{user.email}
								</p>
							</div>
							<button
								onClick={onLogout}
								className="text-[10px] text-zinc-500 hover:text-red-400 transition-colors"
							>
								Sign out
							</button>
						</motion.div>
					)}
				</AnimatePresence>

				{/* Collapsed: sign out icon */}
				{collapsed && (
					<Tooltip content="Sign out" side="right">
						<button
							onClick={onLogout}
							className="mt-1 flex w-full items-center justify-center rounded-lg py-2 text-zinc-500 hover:bg-red-950/40 hover:text-red-400 transition-colors"
						>
							<LogOut className="h-[18px] w-[18px]" />
						</button>
					</Tooltip>
				)}

				{/* Collapse toggle */}
				<button
					onClick={onToggle}
					className="mt-1 flex w-full items-center justify-center rounded-lg py-1.5 text-zinc-500 hover:bg-zinc-800/50 hover:text-zinc-300 transition-colors"
				>
					{collapsed ? (
						<ChevronsRight className="h-4 w-4" />
					) : (
						<div className="flex w-full items-center gap-2 px-2.5">
							<ChevronsLeft className="h-4 w-4" />
							<span className="text-xs">Collapse</span>
						</div>
					)}
				</button>
			</div>
		</motion.aside>
	);
}
