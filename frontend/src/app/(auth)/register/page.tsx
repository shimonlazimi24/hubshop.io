"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Check } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";

import { getGoogleLoginUrl, getTikTokLoginUrl, register } from "@/lib/api";
import { setTokens } from "@/lib/auth";

// --- Inline SVG logos ---
function TikTokLogo({ className }: { className?: string }) {
	return (
		<svg className={className} viewBox="0 0 24 24" fill="none">
			<path
				d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1v-3.5a6.37 6.37 0 00-.79-.05A6.34 6.34 0 003.15 15.2a6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.34-6.34V8.73a8.19 8.19 0 004.76 1.52v-3.4a4.85 4.85 0 01-1-.16z"
				fill="currentColor"
			/>
		</svg>
	);
}

function GoogleLogo({ className }: { className?: string }) {
	return (
		<svg className={className} viewBox="0 0 24 24">
			<path
				d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
				fill="#4285F4"
			/>
			<path
				d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
				fill="#34A853"
			/>
			<path
				d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
				fill="#FBBC05"
			/>
			<path
				d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
				fill="#EA4335"
			/>
		</svg>
	);
}

// --- Password strength ---
type StrengthLevel = "weak" | "medium" | "strong";

function getPasswordStrength(password: string): {
	level: StrengthLevel;
	score: number;
} {
	if (!password) return { level: "weak", score: 0 };
	let score = 0;
	if (password.length >= 8) score++;
	if (password.length >= 12) score++;
	if (/[A-Z]/.test(password)) score++;
	if (/[0-9]/.test(password)) score++;
	if (/[^A-Za-z0-9]/.test(password)) score++;

	if (score <= 2) return { level: "weak", score: 1 };
	if (score <= 3) return { level: "medium", score: 2 };
	return { level: "strong", score: 3 };
}

const STRENGTH_CONFIG: Record<
	StrengthLevel,
	{ color: string; bg: string; label: string }
> = {
	weak: { color: "bg-danger", bg: "bg-danger/20", label: "Weak" },
	medium: { color: "bg-warning", bg: "bg-warning/20", label: "Medium" },
	strong: { color: "bg-success", bg: "bg-success/20", label: "Strong" },
};

function PasswordStrengthBar({ password }: { password: string }) {
	const { level, score } = useMemo(
		() => getPasswordStrength(password),
		[password],
	);
	const config = STRENGTH_CONFIG[level];

	if (!password) return null;

	return (
		<motion.div
			initial={{ opacity: 0, height: 0 }}
			animate={{ opacity: 1, height: "auto" }}
			className="mt-2 space-y-1"
		>
			<div className="flex gap-1">
				{[1, 2, 3].map((i) => (
					<div
						key={i}
						className="h-1 flex-1 rounded-full overflow-hidden bg-zinc-800"
					>
						<motion.div
							initial={{ width: 0 }}
							animate={{ width: i <= score ? "100%" : "0%" }}
							transition={{ duration: 0.3, delay: i * 0.1 }}
							className={`h-full rounded-full ${config.color}`}
						/>
					</div>
				))}
			</div>
			<p
				className={`text-[10px] font-medium ${
					level === "weak"
						? "text-danger"
						: level === "medium"
							? "text-warning"
							: "text-success"
				}`}
			>
				{config.label}
			</p>
		</motion.div>
	);
}

// --- Animation variants ---
const containerVariants = {
	hidden: { opacity: 0 },
	visible: {
		opacity: 1,
		transition: { staggerChildren: 0.05, delayChildren: 0.1 },
	},
};

const itemVariants = {
	hidden: { opacity: 0, y: 12 },
	visible: {
		opacity: 1,
		y: 0,
		transition: {
			duration: 0.4,
			ease: [0.25, 0.46, 0.45, 0.94] as const,
		},
	},
};

export default function RegisterPage() {
	const router = useRouter();
	const [fullName, setFullName] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [orgName, setOrgName] = useState("");
	const [error, setError] = useState("");
	const [loading, setLoading] = useState(false);
	const [socialLoading, setSocialLoading] = useState<string | null>(null);
	const [success, setSuccess] = useState(false);

	async function handleSocialLogin(provider: "tiktok" | "google") {
		setSocialLoading(provider);
		setError("");
		try {
			const fetcher =
				provider === "tiktok" ? getTikTokLoginUrl : getGoogleLoginUrl;
			const { authorize_url } = await fetcher();
			window.location.href = authorize_url;
		} catch (err) {
			setError(
				err instanceof Error ? err.message : `${provider} signup failed`,
			);
			setSocialLoading(null);
		}
	}

	async function handleSubmit(e: React.FormEvent) {
		e.preventDefault();
		setError("");
		setLoading(true);
		try {
			const tokens = await register({
				email,
				password,
				full_name: fullName,
				organization_name: orgName,
			});
			setTokens(tokens.access_token, tokens.refresh_token);
			setSuccess(true);
			setTimeout(() => router.push("/overview"), 600);
		} catch (err) {
			setError(err instanceof Error ? err.message : "Registration failed");
			setLoading(false);
		}
	}

	const inputClassName =
		"mt-1 block w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-white placeholder-zinc-500 transition-shadow focus:border-coral/50 focus:outline-none focus:ring-2 focus:ring-coral/20";

	return (
		<div className="relative min-h-screen flex items-center justify-center bg-zinc-950 overflow-hidden">
			{/* Animated gradient mesh background */}
			<div className="auth-mesh-bg" />

			{/* Success overlay */}
			<AnimatePresence>
				{success && (
					<motion.div
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/80 backdrop-blur-sm"
					>
						<motion.div
							initial={{ scale: 0, opacity: 0 }}
							animate={{ scale: 1, opacity: 1 }}
							transition={{ type: "spring", stiffness: 300, damping: 20 }}
							className="flex h-16 w-16 items-center justify-center rounded-full bg-success/20 border border-success/30"
						>
							<Check className="h-8 w-8 text-success" />
						</motion.div>
					</motion.div>
				)}
			</AnimatePresence>

			<motion.div
				variants={containerVariants}
				initial="hidden"
				animate="visible"
				className="relative z-10 max-w-md w-full space-y-6 p-8 bg-zinc-900/80 backdrop-blur-xl rounded-2xl border border-zinc-800"
			>
				<motion.div variants={itemVariants} className="text-center">
					<h1 className="text-3xl font-bold text-white tracking-tight">
						Frodo
					</h1>
					<p className="mt-1 text-sm text-zinc-400">Create your account</p>
				</motion.div>

				{/* Error with shake animation */}
				<AnimatePresence mode="wait">
					{error && (
						<motion.div
							initial={{ opacity: 0, x: 0 }}
							animate={{ opacity: 1, x: [0, -8, 8, -6, 6, -3, 3, 0] }}
							exit={{ opacity: 0, height: 0 }}
							transition={{ duration: 0.4 }}
							className="bg-red-950/50 border border-red-800/60 text-red-300 px-4 py-3 rounded-lg text-sm"
						>
							{error}
						</motion.div>
					)}
				</AnimatePresence>

				<motion.div variants={itemVariants} className="space-y-3">
					<button
						onClick={() => handleSocialLogin("tiktok")}
						disabled={socialLoading !== null}
						className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-black border border-zinc-700 rounded-lg text-white font-medium hover:bg-zinc-800 hover:border-zinc-600 transition-all disabled:opacity-50"
					>
						<TikTokLogo className="h-5 w-5" />
						{socialLoading === "tiktok"
							? "Redirecting..."
							: "Continue with TikTok"}
					</button>
					<button
						onClick={() => handleSocialLogin("google")}
						disabled={socialLoading !== null}
						className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-white border border-zinc-200 rounded-lg text-zinc-900 font-medium hover:bg-zinc-50 transition-all disabled:opacity-50"
					>
						<GoogleLogo className="h-5 w-5" />
						{socialLoading === "google"
							? "Redirecting..."
							: "Continue with Google"}
					</button>
				</motion.div>

				<motion.div variants={itemVariants} className="flex items-center gap-4">
					<div className="flex-1 h-px bg-zinc-800" />
					<span className="text-xs text-zinc-500 uppercase tracking-wider">
						or
					</span>
					<div className="flex-1 h-px bg-zinc-800" />
				</motion.div>

				<form onSubmit={handleSubmit} className="space-y-4">
					<motion.div variants={itemVariants}>
						<label
							htmlFor="fullName"
							className="block text-sm font-medium text-zinc-300"
						>
							Full Name
						</label>
						<input
							id="fullName"
							type="text"
							required
							value={fullName}
							onChange={(e) => setFullName(e.target.value)}
							className={inputClassName}
						/>
					</motion.div>
					<motion.div variants={itemVariants}>
						<label
							htmlFor="email"
							className="block text-sm font-medium text-zinc-300"
						>
							Email
						</label>
						<input
							id="email"
							type="email"
							required
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							className={inputClassName}
						/>
					</motion.div>
					<motion.div variants={itemVariants}>
						<label
							htmlFor="password"
							className="block text-sm font-medium text-zinc-300"
						>
							Password
						</label>
						<input
							id="password"
							type="password"
							required
							minLength={8}
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							className={inputClassName}
						/>
						<PasswordStrengthBar password={password} />
					</motion.div>
					<motion.div variants={itemVariants}>
						<label
							htmlFor="orgName"
							className="block text-sm font-medium text-zinc-300"
						>
							Organization Name
						</label>
						<input
							id="orgName"
							type="text"
							required
							value={orgName}
							onChange={(e) => setOrgName(e.target.value)}
							placeholder="Your agency or brand name"
							className={inputClassName}
						/>
					</motion.div>
					<motion.div variants={itemVariants}>
						<button
							type="submit"
							disabled={loading}
							className="w-full py-3 px-4 rounded-lg bg-coral text-white font-medium hover:bg-coral-dark transition-colors disabled:opacity-50"
						>
							{loading ? "Creating account..." : "Create account"}
						</button>
					</motion.div>
				</form>

				<motion.p
					variants={itemVariants}
					className="text-center text-sm text-zinc-500"
				>
					Already have an account?{" "}
					<Link
						href="/login"
						className="text-coral hover:text-coral-dark transition-colors"
					>
						Sign in
					</Link>
				</motion.p>
			</motion.div>
		</div>
	);
}
