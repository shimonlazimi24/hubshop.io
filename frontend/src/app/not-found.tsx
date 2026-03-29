import Link from "next/link";

export default function NotFound() {
	return (
		<div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
			<div className="w-full max-w-md text-center">
				<p className="mb-2 text-6xl font-bold text-gray-200">404</p>
				<h1 className="mb-2 text-xl font-semibold text-gray-900">
					Page not found
				</h1>
				<p className="mb-8 text-sm text-gray-500">
					The page you are looking for does not exist or has been moved.
				</p>
				<Link
					href="/overview"
					className="inline-flex rounded-lg bg-gray-900 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-gray-800"
				>
					Back to Overview
				</Link>
			</div>
		</div>
	);
}
