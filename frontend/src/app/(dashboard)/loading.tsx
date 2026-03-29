import { Skeleton } from "@/components/ui/skeleton";

export default function DashboardLoading() {
	return (
		<div className="p-4 md:p-6 lg:p-8">
			{/* Page title skeleton */}
			<Skeleton className="h-7 w-48 mb-6" />

			{/* Metric cards skeleton */}
			<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
				{Array.from({ length: 4 }).map((_, i) => (
					<div
						key={i}
						className="rounded-xl border border-gray-100 bg-white p-6"
					>
						<Skeleton className="h-4 w-24 mb-3" />
						<Skeleton className="h-8 w-16 mb-2" />
						<Skeleton className="h-3 w-32" />
					</div>
				))}
			</div>

			{/* Table / content skeleton */}
			<div className="rounded-xl border border-gray-100 bg-white p-6">
				<Skeleton className="h-5 w-32 mb-4" />
				<div className="space-y-3">
					{Array.from({ length: 5 }).map((_, i) => (
						<div key={i} className="flex items-center gap-4 py-3">
							<Skeleton className="h-4 w-4 rounded-full" />
							<Skeleton className="h-4 flex-1 max-w-48" />
							<Skeleton className="h-4 w-20" />
							<Skeleton className="h-4 w-16" />
						</div>
					))}
				</div>
			</div>
		</div>
	);
}
