"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { getTikTokLoginUrl, getGoogleLoginUrl, register } from "@/lib/api";
import { setTokens } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [orgName, setOrgName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [socialLoading, setSocialLoading] = useState<string | null>(null);

  async function handleSocialLogin(provider: "tiktok" | "google") {
    setSocialLoading(provider);
    setError("");
    try {
      const fetcher = provider === "tiktok" ? getTikTokLoginUrl : getGoogleLoginUrl;
      const { authorize_url } = await fetcher();
      window.location.href = authorize_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : `${provider} signup failed`);
      setSocialLoading(null);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const tokens = await register({ email, password, full_name: fullName, organization_name: orgName });
      setTokens(tokens.access_token, tokens.refresh_token);
      router.push("/overview");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950">
      <div className="max-w-md w-full space-y-6 p-8 bg-zinc-900 rounded-2xl border border-zinc-800">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white tracking-tight">Frodo</h1>
          <p className="mt-1 text-sm text-zinc-400">Create your account</p>
        </div>

        {error && (
          <div className="bg-red-950/50 border border-red-800 text-red-300 px-4 py-3 rounded-lg text-sm">{error}</div>
        )}

        <div className="space-y-3">
          <button onClick={() => handleSocialLogin("tiktok")} disabled={socialLoading !== null}
            className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-black border border-zinc-700 rounded-lg text-white font-medium hover:bg-zinc-800 transition-colors disabled:opacity-50">
            {socialLoading === "tiktok" ? "Redirecting..." : "Continue with TikTok"}
          </button>
          <button onClick={() => handleSocialLogin("google")} disabled={socialLoading !== null}
            className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-white border border-zinc-200 rounded-lg text-zinc-900 font-medium hover:bg-zinc-50 transition-colors disabled:opacity-50">
            {socialLoading === "google" ? "Redirecting..." : "Continue with Google"}
          </button>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex-1 h-px bg-zinc-800" />
          <span className="text-xs text-zinc-500 uppercase tracking-wider">or</span>
          <div className="flex-1 h-px bg-zinc-800" />
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="fullName" className="block text-sm font-medium text-zinc-300">Full Name</label>
            <input id="fullName" type="text" required value={fullName} onChange={(e) => setFullName(e.target.value)}
              className="mt-1 block w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-white placeholder-zinc-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500" />
          </div>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-zinc-300">Email</label>
            <input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-white placeholder-zinc-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500" />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-zinc-300">Password</label>
            <input id="password" type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-white placeholder-zinc-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500" />
          </div>
          <div>
            <label htmlFor="orgName" className="block text-sm font-medium text-zinc-300">Organization Name</label>
            <input id="orgName" type="text" required value={orgName} onChange={(e) => setOrgName(e.target.value)} placeholder="Your agency or brand name"
              className="mt-1 block w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-white placeholder-zinc-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500" />
          </div>
          <button type="submit" disabled={loading}
            className="w-full py-3 px-4 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-500 transition-colors disabled:opacity-50">
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="text-center text-sm text-zinc-500">
          Already have an account?{" "}
          <Link href="/login" className="text-blue-400 hover:text-blue-300">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
