"use client";

import { useState } from "react";
import Link from "next/link";
import { Radio, Eye, Gift, MessageCircle, Clock, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

interface LiveSession {
  id: string;
  streamer_username: string;
  streamer_display_name: string;
  status: "monitoring" | "ended" | "error";
  viewer_count: number;
  gift_count: number;
  comment_count: number;
  started_at: string;
  duration_minutes: number;
}

const STATUS_CONFIG = {
  monitoring: { label: "Monitoring", color: "bg-green-100 text-green-800", dot: "bg-green-500" },
  ended: { label: "Ended", color: "bg-gray-100 text-gray-800", dot: "bg-gray-400" },
  error: { label: "Error", color: "bg-red-100 text-red-800", dot: "bg-red-500" },
};

const MOCK_SESSIONS: LiveSession[] = [
  {
    id: "sess-1",
    streamer_username: "beauty_live",
    streamer_display_name: "Beauty LIVE",
    status: "monitoring",
    viewer_count: 12_400,
    gift_count: 342,
    comment_count: 1_890,
    started_at: "2026-02-20T09:30:00Z",
    duration_minutes: 45,
  },
  {
    id: "sess-2",
    streamer_username: "shop_showcase",
    streamer_display_name: "Shop Showcase",
    status: "monitoring",
    viewer_count: 8_900,
    gift_count: 156,
    comment_count: 987,
    started_at: "2026-02-20T10:00:00Z",
    duration_minutes: 15,
  },
  {
    id: "sess-3",
    streamer_username: "gaming_tt",
    streamer_display_name: "GameTime",
    status: "ended",
    viewer_count: 34_500,
    gift_count: 892,
    comment_count: 4_560,
    started_at: "2026-02-20T06:00:00Z",
    duration_minutes: 180,
  },
  {
    id: "sess-4",
    streamer_username: "music_live_show",
    streamer_display_name: "Music Live",
    status: "error",
    viewer_count: 0,
    gift_count: 0,
    comment_count: 0,
    started_at: "2026-02-20T08:00:00Z",
    duration_minutes: 2,
  },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export default function LiveOverviewPage() {
  const [sessions] = useState<LiveSession[]>(MOCK_SESSIONS);

  const activeCount = sessions.filter((s) => s.status === "monitoring").length;

  return (
    <div className="max-w-6xl">
      {/* Stats Bar */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm text-gray-600">
              {activeCount} active stream{activeCount !== 1 ? "s" : ""}
            </span>
          </div>
          <span className="text-sm text-gray-400">
            {sessions.length} total session{sessions.length !== 1 ? "s" : ""}
          </span>
        </div>
        <Link
          href="/live/monitor"
          className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Monitor Stream
        </Link>
      </div>

      {/* Sessions List */}
      <div className="space-y-3">
        {sessions.map((session) => {
          const statusConfig = STATUS_CONFIG[session.status];
          return (
            <Link
              key={session.id}
              href={`/live/${session.id}`}
              className="block rounded-xl border border-gray-100 bg-white p-5 hover:shadow-md hover:border-gray-200 transition-all duration-200"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                    <Radio className={cn("h-5 w-5", session.status === "monitoring" ? "text-coral" : "text-gray-400")} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-gray-900">{session.streamer_display_name}</p>
                      <span className={cn("inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full", statusConfig.color)}>
                        <span className={cn("h-1.5 w-1.5 rounded-full", statusConfig.dot)} />
                        {statusConfig.label}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">@{session.streamer_username}</p>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-1.5">
                    <Eye className="h-4 w-4 text-gray-400" />
                    <span className="text-sm text-gray-600">{formatNumber(session.viewer_count)}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Gift className="h-4 w-4 text-gray-400" />
                    <span className="text-sm text-gray-600">{formatNumber(session.gift_count)}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <MessageCircle className="h-4 w-4 text-gray-400" />
                    <span className="text-sm text-gray-600">{formatNumber(session.comment_count)}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Clock className="h-4 w-4 text-gray-400" />
                    <span className="text-sm text-gray-500">{session.duration_minutes}m</span>
                  </div>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {sessions.length === 0 && (
        <div className="rounded-xl border border-gray-100 bg-white py-12 text-center">
          <Radio className="h-8 w-8 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-500">No active monitoring sessions</p>
          <p className="text-xs text-gray-400 mt-1">Start monitoring a LIVE stream to see events in real-time</p>
        </div>
      )}
    </div>
  );
}
