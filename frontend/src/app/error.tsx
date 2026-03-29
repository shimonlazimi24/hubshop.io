"use client";

import { useEffect } from "react";

export default function GlobalError({
	error,
	reset,
}: {
	error: Error & { digest?: string };
	reset: () => void;
}) {
	useEffect(() => {
		console.error("Unhandled error:", error);
	}, [error]);

	return (
		<div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
			<div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-8 text-center shadow-sm">
				<div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-50">
					<svg
						className="h-6 w-6 text-red-500"
						fill="none"
						viewBox="0 0 24 24"
						strokeWidth={1.5}
						stroke="currentColor"
					>
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
						/>
					</svg>
				</div>

				<h1 className="mb-2 text-xl font-semibold text-gray-900">
					Something went wrong
				</h1>
				<p className="mb-6 text-sm text-gray-500">
					An unexpected error occurred. Please try again or return to the home
					page.
				</p>

				<div className="flex items-center justify-center gap-3">
					<button
						onClick={reset}
						className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-gray-800"
					>
						Try Again
					</button>
					<a
						href="/overview"
						className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
					>
						Go Home
					</a>
				</div>
			</div>
		</div>
	);
}
