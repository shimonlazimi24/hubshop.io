"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Radio, User, AlertCircle } from "lucide-react";

export default function MonitorStreamPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState("");

  function handleStart() {
    if (!username.trim()) return;
    setStarting(true);
    setError("");
    // Simulate starting a monitoring session
    setTimeout(() => {
      setStarting(false);
      // Navigate to the session page with a mock session ID
      router.push(`/live/sess-new`);
    }, 1000);
  }

  return (
    <div className="max-w-xl">
      <div className="rounded-xl border border-gray-100 bg-white p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-coral/10">
            <Radio className="h-5 w-5 text-coral" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-gray-900">Start Monitoring</h2>
            <p className="text-xs text-gray-500">Enter a TikTok username to start monitoring their LIVE stream</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">
              TikTok Username
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleStart()}
                placeholder="@username"
                className="w-full pl-9 pr-3 py-2.5 border border-gray-300 rounded-md text-sm"
              />
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 rounded-lg">
              <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <button
            onClick={handleStart}
            disabled={starting || !username.trim()}
            className="w-full rounded-lg bg-coral px-4 py-2.5 text-sm font-medium text-white hover:bg-coral/90 disabled:opacity-50 transition-colors"
          >
            {starting ? "Starting..." : "Start Monitoring"}
          </button>
        </div>

        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-xs font-medium text-gray-700 mb-2">How it works</h3>
          <ul className="space-y-1.5">
            <li className="text-xs text-gray-500 flex items-start gap-2">
              <span className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-gray-200 text-[10px] font-medium text-gray-600 flex-shrink-0 mt-0.5">1</span>
              Enter the TikTok username of the streamer
            </li>
            <li className="text-xs text-gray-500 flex items-start gap-2">
              <span className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-gray-200 text-[10px] font-medium text-gray-600 flex-shrink-0 mt-0.5">2</span>
              Frodo connects to the LIVE stream via WebSocket
            </li>
            <li className="text-xs text-gray-500 flex items-start gap-2">
              <span className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-gray-200 text-[10px] font-medium text-gray-600 flex-shrink-0 mt-0.5">3</span>
              Comments, gifts, likes, and follows are captured in real-time
            </li>
            <li className="text-xs text-gray-500 flex items-start gap-2">
              <span className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-gray-200 text-[10px] font-medium text-gray-600 flex-shrink-0 mt-0.5">4</span>
              View post-stream analytics after the session ends
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
