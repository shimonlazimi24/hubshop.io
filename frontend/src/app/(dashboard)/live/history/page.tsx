"use client";

import { useState } from "react";
import Link from "next/link";
import { Clock, Eye, Gift, DollarSign } from "lucide-react";

interface PastSession {
  id: string;
  streamer_username: string;
  streamer_display_name: string;
  date: string;
  duration_minutes: number;
  total_viewers: number;
  peak_viewers: number;
  gift_revenue: number;
  total_comments: number;
}

const MOCK_HISTORY: PastSession[] = [
  {
    id: "hist-1",
    streamer_username: "beauty_live",
    streamer_display_name: "Beauty LIVE",
    date: "2026-02-20T09:30:00Z",
    duration_minutes: 120,
    total_viewers: 34_500,
    peak_viewers: 12_400,
    gift_revenue: 2_890.50,
    total_comments: 4_560,
  },
  {
    id: "hist-2",
    streamer_username: "shop_showcase",
    streamer_display_name: "Shop Showcase",
    date: "2026-02-19T14:00:00Z",
    duration_minutes: 90,
    total_viewers: 22_100,
    peak_viewers: 8_900,
    gift_revenue: 1_450.00,
    total_comments: 2_890,
  },
  {
    id: "hist-3",
    streamer_username: "gaming_tt",
    streamer_display_name: "GameTime",
    date: "2026-02-18T20:00:00Z",
    duration_minutes: 240,
    total_viewers: 67_800,
    peak_viewers: 28_900,
    gift_revenue: 5_670.00,
    total_comments: 12_340,
  },
  {
    id: "hist-4",
    streamer_username: "cooking_live",
    streamer_display_name: "Cook With Us",
    date: "2026-02-17T11:00:00Z",
    duration_minutes: 60,
    total_viewers: 15_200,
    peak_viewers: 6_700,
    gift_revenue: 890.00,
    total_comments: 1_780,
  },
  {
    id: "hist-5",
    streamer_username: "music_live_show",
    streamer_display_name: "Music Live",
    date: "2026-02-16T19:00:00Z",
    duration_minutes: 150,
    total_viewers: 45_600,
    peak_viewers: 18_200,
    gift_revenue: 3_450.00,
    total_comments: 8_900,
  },
  {
    id: "hist-6",
    streamer_username: "fitness_stream",
    streamer_display_name: "FitLive",
    date: "2026-02-15T07:00:00Z",
    duration_minutes: 45,
    total_viewers: 8_900,
    peak_viewers: 3_200,
    gift_revenue: 340.00,
    total_comments: 567,
  },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function formatDuration(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h === 0) return `${m}m`;
  if (m === 0) return `${h}h`;
  return `${h}h ${m}m`;
}

export default function LiveHistoryPage() {
  const [history] = useState<PastSession[]>(MOCK_HISTORY);

  return (
    <div className="max-w-6xl">
      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Streamer</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Duration</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Total Viewers</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Gift Revenue</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {history.map((session) => (
              <tr key={session.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <p className="text-sm font-medium text-gray-900">{session.streamer_display_name}</p>
                  <p className="text-xs text-gray-500">@{session.streamer_username}</p>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {new Date(session.date).toLocaleDateString()}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <Clock className="h-3.5 w-3.5 text-gray-400" />
                    <span className="text-sm text-gray-600">{formatDuration(session.duration_minutes)}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <Eye className="h-3.5 w-3.5 text-gray-400" />
                    <span className="text-sm text-gray-600">{formatNumber(session.total_viewers)}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <DollarSign className="h-3.5 w-3.5 text-green-500" />
                    <span className="text-sm font-medium text-gray-900">
                      ${session.gift_revenue.toLocaleString()}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <Link
                    href={`/live/${session.id}/analytics`}
                    className="text-sm text-blue-600 hover:underline"
                  >
                    View Analytics
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {history.length === 0 && (
          <div className="px-4 py-8 text-center text-gray-500">
            No past LIVE sessions found
          </div>
        )}
      </div>
    </div>
  );
}
