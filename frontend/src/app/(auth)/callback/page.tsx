"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, Suspense } from "react";

import { socialCallback } from "@/lib/api";
import { setTokens } from "@/lib/auth";

function CallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState("");

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");
    const provider = searchParams.get("provider") as "tiktok" | "google" | null;

    if (!code || !provider) {
      setError("Invalid callback — missing code or provider");
      return;
    }

    socialCallback(provider, code, state || undefined)
      .then((tokens) => {
        setTokens(tokens.access_token, tokens.refresh_token);
        router.push("/overview");
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Login failed");
      });
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950">
        <div className="max-w-md w-full p-8 bg-zinc-900 rounded-2xl border border-zinc-800 text-center">
          <h1 className="text-xl font-bold text-red-400">Login Failed</h1>
          <p className="mt-2 text-sm text-zinc-400">{error}</p>
          <a href="/login" className="mt-4 inline-block text-blue-400 hover:text-blue-300">Back to login</a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto" />
        <p className="mt-4 text-zinc-400">Completing login...</p>
      </div>
    </div>
  );
}

export default function CallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-zinc-950">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white" />
      </div>
    }>
      <CallbackHandler />
    </Suspense>
  );
}
