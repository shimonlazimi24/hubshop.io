"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
	ChevronDown,
	ChevronRight,
	LogOut,
	Moon,
	Search,
	Settings,
	Sun,
	User,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import type { UserResponse } from "@/lib/api";
import { cn } from "@/lib/utils";
import { MobileNav } from "./mobile-nav";
import { NotificationBell } from "./notification-bell";

function useBreadcrumbs() {
	const pathname = usePathname();
	const segments = pathname.split("/").filter(Boolean);

	return segments.map((segment, index) => {
		const href = `/${segments.slice(0, index + 1).join("/")}`;
		const isId = /^[0-9a-f-]{8,}$/i.test(segment);
		const label = isId
			? `#${segment.slice(0, 8)}`
			: segment.replace(/[-_]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

		return { label, href, isLast: index === segments.length - 1 };
	});
}

function useThemeToggle() {
	const [isDark, setIsDark] = useState(false);

	useEffect(() => {
		const root = document.documentElement;
		setIsDark(root.classList.contains("dark"));
	}, []);

	const toggle = useCallback(() => {
		const root = document.documentElement;
		const next = !root.classList.contains("dark");
		root.classList.toggle("dark", next);
		setIsDark(next);
		try {
			localStorage.setItem("frodo_theme", next ? "dark" : "light");
		} catch {
			// localStorage may be unavailable
		}
	}, []);

	// Restore theme on mount
	useEffect(() => {
		try {
			const stored = localStorage.getItem("frodo_theme");
			if (stored === "dark") {
				document.documentElement.classList.add("dark");
				setIsDark(true);
			} else if (stored === "light") {
				document.documentElement.classList.remove("dark");
				setIsDark(false);
			} else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
				document.documentElement.classList.add("dark");
				setIsDark(true);
			}
		} catch {
			// ignore
		}
	}, []);

	return { isDark, toggle };
}

interface UserAvatarDropdownProps {
	user: UserResponse | null;
	onLogout: () => void;
}

function UserAvatarDropdown({ user, onLogout }: UserAvatarDropdownProps) {
	const [open, setOpen] = useState(false);
	const dropdownRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (!open) return;
		function handleClickOutside(e: MouseEvent) {
			if (
				dropdownRef.current &&
				!dropdownRef.current.contains(e.target as Node)
			) {
				setOpen(false);
			}
		}
		function handleKeyDown(e: KeyboardEvent) {
			if (e.key === "Escape") setOpen(false);
		}
		document.addEventListener("mousedown", handleClickOutside);
		document.addEventListener("keydown", handleKeyDown);
		return () => {
			document.removeEventListener("mousedown", handleClickOutside);
			document.removeEventListener("keydown", handleKeyDown);
		};
	}, [open]);

	if (!user) return null;

	const initials =
		user.full_name
			?.split(" ")
			.map((n) => n.charAt(0))
			.join("")
			.toUpperCase()
			.slice(0, 2) || "U";

	return (
		<div ref={dropdownRef} className="relative">
			<button
				onClick={() => setOpen((p) => !p)}
				className="flex items-center gap-2 rounded-lg px-1.5 py-1 hover:bg-gray-100 dark:hover:bg-zinc-800 transition-colors"
				aria-label="User menu"
			>
				<div className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-coral to-purple text-[11px] font-semibold text-white">
					{initials}
				</div>
				<ChevronDown
					className={cn(
						"h-3 w-3 text-gray-400 dark:text-zinc-500 transition-transform duration-150",
						open && "rotate-180",
					)}
				/>
			</button>

			<AnimatePresence>
				{open && (
					<motion.div
						initial={{ opacity: 0, y: -4, scale: 0.95 }}
						animate={{ opacity: 1, y: 0, scale: 1 }}
						exit={{ opacity: 0, y: -4, scale: 0.95 }}
						transition={{ duration: 0.12 }}
						className="absolute right-0 top-full z-50 mt-2 w-56 overflow-hidden rounded-xl border border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 shadow-lg"
					>
						{/* User info */}
						<div className="border-b border-gray-100 dark:border-zinc-800 px-4 py-3">
							<p className="text-sm font-medium text-gray-900 dark:text-zinc-100 truncate">
								{user.full_name}
							</p>
							<p className="text-xs text-gray-400 dark:text-zinc-500 truncate">
								{user.email}
							</p>
						</div>

						{/* Menu items */}
						<div className="py-1">
							<Link
								href="/settings"
								onClick={() => setOpen(false)}
								className="flex items-center gap-2.5 px-4 py-2 text-sm text-gray-600 dark:text-zinc-400 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors"
							>
								<Settings className="h-3.5 w-3.5" />
								Settings
							</Link>
							<Link
								href="/settings"
								onClick={() => setOpen(false)}
								className="flex items-center gap-2.5 px-4 py-2 text-sm text-gray-600 dark:text-zinc-400 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors"
							>
								<User className="h-3.5 w-3.5" />
								Profile
							</Link>
						</div>

						{/* Sign out */}
						<div className="border-t border-gray-100 dark:border-zinc-800 py-1">
							<button
								onClick={() => {
									setOpen(false);
									onLogout();
								}}
								className="flex w-full items-center gap-2.5 px-4 py-2 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
							>
								<LogOut className="h-3.5 w-3.5" />
								Sign out
							</button>
						</div>
					</motion.div>
				)}
			</AnimatePresence>
		</div>
	);
}

interface TopBarProps {
	onOpenCommandPalette: () => void;
	user: UserResponse | null;
	onLogout: () => void;
}

export function TopBar({ onOpenCommandPalette, user, onLogout }: TopBarProps) {
	const breadcrumbs = useBreadcrumbs();
	const [isMac, setIsMac] = useState(false);
	const { isDark, toggle: toggleTheme } = useThemeToggle();

	useEffect(() => {
		setIsMac(/Mac/i.test(navigator.userAgent));
	}, []);

	return (
		<header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-gray-100 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md px-4 md:px-6">
			{/* Left: Mobile nav + Breadcrumbs */}
			<div className="flex items-center gap-3">
				<MobileNav user={user} onLogout={onLogout} />

				<nav className="hidden md:flex items-center gap-1 text-sm">
					{breadcrumbs.map((crumb, i) => (
						<div key={crumb.href} className="flex items-center gap-1">
							{i > 0 && (
								<ChevronRight className="h-3.5 w-3.5 text-gray-300 dark:text-zinc-600" />
							)}
							{crumb.isLast ? (
								<span className="font-medium text-gray-900 dark:text-zinc-100">
									{crumb.label}
								</span>
							) : (
								<Link
									href={crumb.href}
									className="text-gray-400 dark:text-zinc-500 hover:text-gray-600 dark:hover:text-zinc-300 transition-colors"
								>
									{crumb.label}
								</Link>
							)}
						</div>
					))}
				</nav>
			</div>

			{/* Right: Search + Theme toggle + Notifications + User */}
			<div className="flex items-center gap-2">
				{/* Search trigger */}
				<button
					onClick={onOpenCommandPalette}
					className={cn(
						"flex items-center gap-2 rounded-lg border border-gray-200 dark:border-zinc-700 px-3 py-1.5 text-sm text-gray-400 dark:text-zinc-500 hover:border-gray-300 dark:hover:border-zinc-600 hover:text-gray-500 dark:hover:text-zinc-400 transition-colors",
						"hidden sm:flex",
					)}
				>
					<Search className="h-3.5 w-3.5" />
					<span>Search...</span>
					<kbd className="ml-2 rounded border border-gray-200 dark:border-zinc-700 bg-gray-50 dark:bg-zinc-800 px-1.5 py-0.5 text-[10px] font-medium text-gray-400 dark:text-zinc-500">
						{isMac ? "\u2318" : "Ctrl+"}K
					</kbd>
				</button>

				{/* Mobile search button */}
				<button
					onClick={onOpenCommandPalette}
					className="flex sm:hidden h-9 w-9 items-center justify-center rounded-lg text-gray-400 dark:text-zinc-500 hover:bg-gray-100 dark:hover:bg-zinc-800 transition-colors"
					aria-label="Search"
				>
					<Search className="h-4 w-4" />
				</button>

				{/* Theme toggle */}
				<button
					onClick={toggleTheme}
					className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-400 dark:text-zinc-500 hover:bg-gray-100 dark:hover:bg-zinc-800 hover:text-gray-600 dark:hover:text-zinc-300 transition-colors"
					aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
				>
					{isDark ? (
						<Sun className="h-[18px] w-[18px]" />
					) : (
						<Moon className="h-[18px] w-[18px]" />
					)}
				</button>

				{/* Notification bell */}
				<NotificationBell />

				{/* User avatar dropdown */}
				<UserAvatarDropdown user={user} onLogout={onLogout} />
			</div>
		</header>
	);
}
