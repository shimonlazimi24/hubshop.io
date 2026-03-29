"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
	ChevronDown,
	ChevronLeft,
	ChevronRight,
	ChevronsUpDown,
	ChevronUp,
	FileX2,
	Inbox,
	Search,
} from "lucide-react";
import { type ReactNode, useState } from "react";
import { cn } from "@/lib/utils";

export interface Column<T> {
	key: string;
	header: string;
	sortable?: boolean;
	className?: string;
	render: (row: T, index: number) => ReactNode;
}

interface DataTableProps<T> {
	columns: Column<T>[];
	data: T[];
	keyExtractor: (row: T) => string;
	onRowClick?: (row: T) => void;
	emptyTitle?: string;
	emptyDescription?: string;
	emptyAction?: { label: string; onClick: () => void };
	page?: number;
	totalPages?: number;
	onPageChange?: (page: number) => void;
	loading?: boolean;
	className?: string;
}

// --- Enhanced illustrated empty state ---
function TableEmptyState({
	title,
	description,
	action,
}: {
	title: string;
	description?: string;
	action?: { label: string; onClick: () => void };
}) {
	return (
		<motion.div
			initial={{ opacity: 0, y: 8 }}
			animate={{ opacity: 1, y: 0 }}
			transition={{ duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] }}
			className="flex flex-col items-center justify-center py-20 px-4 text-center"
		>
			{/* Composed icon illustration */}
			<div className="relative mb-6">
				<div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-zinc-800/60 border border-zinc-700/50">
					<Inbox className="h-7 w-7 text-zinc-500" />
				</div>
				<div className="absolute -right-2 -top-2 flex h-7 w-7 items-center justify-center rounded-lg bg-zinc-800 border border-zinc-700/50">
					<Search className="h-3.5 w-3.5 text-zinc-500" />
				</div>
				<div className="absolute -left-2 -bottom-1 flex h-6 w-6 items-center justify-center rounded-md bg-zinc-800 border border-zinc-700/50">
					<FileX2 className="h-3 w-3 text-zinc-600" />
				</div>
			</div>
			<h3 className="text-sm font-semibold text-zinc-200 mb-1">{title}</h3>
			{description && (
				<p className="text-sm text-zinc-500 max-w-xs mb-5">{description}</p>
			)}
			{action && (
				<button
					onClick={action.onClick}
					className="inline-flex items-center gap-1.5 rounded-lg bg-coral px-4 py-2 text-sm font-medium text-white hover:bg-coral-dark transition-colors"
				>
					{action.label}
				</button>
			)}
		</motion.div>
	);
}

// --- Sort indicator with animation ---
function SortIndicator({
	active,
	direction,
}: {
	active: boolean;
	direction: "asc" | "desc";
}) {
	if (!active) {
		return <ChevronsUpDown className="h-3.5 w-3.5 text-zinc-600" />;
	}
	return (
		<motion.div
			key={direction}
			initial={{ rotate: direction === "desc" ? -180 : 180, opacity: 0 }}
			animate={{ rotate: 0, opacity: 1 }}
			transition={{ duration: 0.2, ease: "easeOut" }}
		>
			{direction === "asc" ? (
				<ChevronUp className="h-3.5 w-3.5 text-coral" />
			) : (
				<ChevronDown className="h-3.5 w-3.5 text-coral" />
			)}
		</motion.div>
	);
}

export function DataTable<T>({
	columns,
	data,
	keyExtractor,
	onRowClick,
	emptyTitle = "No data found",
	emptyDescription,
	emptyAction,
	page,
	totalPages,
	onPageChange,
	loading = false,
	className,
}: DataTableProps<T>) {
	const [sortKey, setSortKey] = useState<string | null>(null);
	const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

	function handleSort(key: string) {
		if (sortKey === key) {
			setSortDir((d) => (d === "asc" ? "desc" : "asc"));
		} else {
			setSortKey(key);
			setSortDir("asc");
		}
	}

	if (!loading && data.length === 0) {
		return (
			<div className="rounded-lg border border-zinc-800 bg-zinc-900">
				<TableEmptyState
					title={emptyTitle}
					description={emptyDescription}
					action={emptyAction}
				/>
			</div>
		);
	}

	return (
		<div
			className={cn(
				"rounded-lg border border-zinc-800 bg-zinc-900 overflow-hidden",
				className,
			)}
		>
			<div className="overflow-x-auto">
				<table className="w-full text-sm">
					<thead>
						<tr className="border-b border-zinc-800 bg-zinc-900/80">
							{columns.map((col) => (
								<th
									key={col.key}
									className={cn(
										"px-4 py-3 text-left text-xs font-semibold text-zinc-400 uppercase tracking-wider",
										col.sortable &&
											"cursor-pointer select-none hover:text-zinc-200 transition-colors",
										col.className,
									)}
									onClick={col.sortable ? () => handleSort(col.key) : undefined}
								>
									<span className="flex items-center gap-1">
										{col.header}
										{col.sortable && (
											<SortIndicator
												active={sortKey === col.key}
												direction={sortDir}
											/>
										)}
									</span>
								</th>
							))}
						</tr>
					</thead>
					<tbody className="divide-y divide-zinc-800/60">
						{loading
							? Array.from({ length: 5 }).map((_, i) => (
									<tr key={`skeleton-${i}`}>
										{columns.map((col) => (
											<td key={col.key} className="px-4 py-3">
												<div className="relative h-4 w-24 rounded bg-zinc-800/50 overflow-hidden">
													<div
														className="absolute inset-0"
														style={{
															background:
																"linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.04) 50%, transparent 100%)",
															animation: `shimmer-sweep 1.8s ease-in-out infinite`,
															animationDelay: `${i * 100}ms`,
														}}
													/>
												</div>
											</td>
										))}
									</tr>
								))
							: data.map((row, idx) => (
									<motion.tr
										key={keyExtractor(row)}
										initial={{ opacity: 0, x: -8 }}
										animate={{ opacity: 1, x: 0 }}
										transition={{
											duration: 0.3,
											delay: Math.min(idx * 0.04, 0.4),
											ease: [0.25, 0.46, 0.45, 0.94],
										}}
										onClick={onRowClick ? () => onRowClick(row) : undefined}
										className={cn(
											"group relative transition-colors",
											onRowClick && "cursor-pointer hover:bg-zinc-800/50",
										)}
									>
										{/* Left border highlight on hover */}
										<td className="absolute left-0 top-0 bottom-0 w-0.5">
											<div className="h-full w-full bg-coral scale-y-0 group-hover:scale-y-100 transition-transform duration-200 origin-center" />
										</td>
										{columns.map((col) => (
											<td
												key={col.key}
												className={cn("px-4 py-3 text-zinc-300", col.className)}
											>
												{col.render(row, idx)}
											</td>
										))}
									</motion.tr>
								))}
					</tbody>
				</table>
			</div>

			{/* Pagination */}
			{page !== undefined &&
				totalPages !== undefined &&
				totalPages > 1 &&
				onPageChange && (
					<div className="flex items-center justify-between border-t border-zinc-800 px-4 py-3">
						<AnimatePresence mode="wait">
							<motion.p
								key={page}
								initial={{ opacity: 0, y: 4 }}
								animate={{ opacity: 1, y: 0 }}
								exit={{ opacity: 0, y: -4 }}
								transition={{ duration: 0.15 }}
								className="text-xs text-zinc-500 tabular-nums"
							>
								Page {page} of {totalPages}
							</motion.p>
						</AnimatePresence>
						<div className="flex items-center gap-1">
							<button
								disabled={page <= 1}
								onClick={() => onPageChange(page - 1)}
								className="flex h-8 w-8 items-center justify-center rounded-lg text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
							>
								<ChevronLeft className="h-4 w-4" />
							</button>
							<button
								disabled={page >= totalPages}
								onClick={() => onPageChange(page + 1)}
								className="flex h-8 w-8 items-center justify-center rounded-lg text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
							>
								<ChevronRight className="h-4 w-4" />
							</button>
						</div>
					</div>
				)}
		</div>
	);
}
