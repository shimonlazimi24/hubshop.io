"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Eye,
  Users,
  Gift,
  TrendingUp,
  MessageCircle,
  DollarSign,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface TopContributor {
  rank: number;
  username: string;
  count: number;
  value?: number;
}

const MOCK_KPI = {
  total_viewers: 34_500,
  peak_concurrent: 12_400,
  gift_revenue: 2_890.50,
  engagement_rate: 8.7,
  total_comments: 4_560,
  total_likes: 18_900,
  total_shares: 1_230,
  duration_minutes: 180,
};

const TOP_COMMENTERS: TopContributor[] = [
  { rank: 1, username: "super_fan_1", count: 45 },
  { rank: 2, username: "beauty_lover", count: 38 },
  { rank: 3, username: "deal_hunter_tt", count: 32 },
  { rank: 4, username: "shopper_99", count: 28 },
  { rank: 5, username: "first_timer_live", count: 24 },
  { rank: 6, username: "regular_viewer", count: 21 },
  { rank: 7, username: "chat_king", count: 19 },
  { rank: 8, username: "question_asker", count: 17 },
];

const TOP_GIFTERS: TopContributor[] = [
  { rank: 1, username: "vip_supporter", count: 12, value: 890.00 },
  { rank: 2, username: "big_spender", count: 8, value: 650.00 },
  { rank: 3, username: "generous_one", count: 15, value: 420.00 },
  { rank: 4, username: "gift_fairy", count: 6, value: 310.00 },
  { rank: 5, username: "top_fan", count: 9, value: 280.00 },
  { rank: 6, username: "whale_viewer", count: 3, value: 190.00 },
  { rank: 7, username: "kind_heart", count: 4, value: 95.00 },
  { rank: 8, username: "supporter_tt", count: 2, value: 55.50 },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export default function LiveSessionAnalyticsPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  return (
    <div className="max-w-4xl">
      <button
        onClick={() => router.back()}
        className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Event Feed
      </button>

      <div className="flex items-center gap-2 mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Post-Stream Analytics</h2>
        <span className="text-sm text-gray-400">Session: {sessionId}</span>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="rounded-xl border border-gray-100 bg-white p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-purple/5 border border-purple/10">
              <Eye className="h-[18px] w-[18px] text-purple" />
            </div>
          </div>
          <p className="text-2xl font-semibold text-gray-900">{formatNumber(MOCK_KPI.total_viewers)}</p>
          <p className="text-xs text-gray-400 mt-1">Total Viewers</p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 border border-blue-100">
              <Users className="h-[18px] w-[18px] text-blue-500" />
            </div>
          </div>
          <p className="text-2xl font-semibold text-gray-900">{formatNumber(MOCK_KPI.peak_concurrent)}</p>
          <p className="text-xs text-gray-400 mt-1">Peak Concurrent</p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-yellow-50 border border-yellow-100">
              <DollarSign className="h-[18px] w-[18px] text-yellow-500" />
            </div>
          </div>
          <p className="text-2xl font-semibold text-gray-900">${MOCK_KPI.gift_revenue.toLocaleString()}</p>
          <p className="text-xs text-gray-400 mt-1">Gift Revenue</p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-green-50 border border-green-100">
              <TrendingUp className="h-[18px] w-[18px] text-green-500" />
            </div>
          </div>
          <p className="text-2xl font-semibold text-gray-900">{MOCK_KPI.engagement_rate}%</p>
          <p className="text-xs text-gray-400 mt-1">Engagement Rate</p>
        </div>
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-4 gap-3 mb-8">
        <div className="rounded-lg bg-gray-50 p-3 text-center">
          <p className="text-sm font-semibold text-gray-900">{formatNumber(MOCK_KPI.total_comments)}</p>
          <p className="text-xs text-gray-500">Comments</p>
        </div>
        <div className="rounded-lg bg-gray-50 p-3 text-center">
          <p className="text-sm font-semibold text-gray-900">{formatNumber(MOCK_KPI.total_likes)}</p>
          <p className="text-xs text-gray-500">Likes</p>
        </div>
        <div className="rounded-lg bg-gray-50 p-3 text-center">
          <p className="text-sm font-semibold text-gray-900">{formatNumber(MOCK_KPI.total_shares)}</p>
          <p className="text-xs text-gray-500">Shares</p>
        </div>
        <div className="rounded-lg bg-gray-50 p-3 text-center">
          <p className="text-sm font-semibold text-gray-900">{MOCK_KPI.duration_minutes}m</p>
          <p className="text-xs text-gray-500">Duration</p>
        </div>
      </div>

      {/* Top Contributors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Commenters */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-4 py-3 border-b border-gray-200 flex items-center gap-2">
            <MessageCircle className="h-4 w-4 text-blue-500" />
            <h3 className="text-sm font-medium text-gray-900">Top Commenters</h3>
          </div>
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100 text-left">
                <th className="px-4 py-2 text-xs font-medium text-gray-500 uppercase w-12">#</th>
                <th className="px-4 py-2 text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="px-4 py-2 text-xs font-medium text-gray-500 uppercase text-right">Comments</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {TOP_COMMENTERS.map((user) => (
                <tr key={user.rank} className="hover:bg-gray-50">
                  <td className="px-4 py-2">
                    <span className={cn(
                      "inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium",
                      user.rank <= 3 ? "bg-coral/10 text-coral" : "bg-gray-100 text-gray-500"
                    )}>
                      {user.rank}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-900">@{user.username}</td>
                  <td className="px-4 py-2 text-sm text-gray-600 text-right">{user.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Top Gifters */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-4 py-3 border-b border-gray-200 flex items-center gap-2">
            <Gift className="h-4 w-4 text-yellow-500" />
            <h3 className="text-sm font-medium text-gray-900">Top Gifters</h3>
          </div>
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100 text-left">
                <th className="px-4 py-2 text-xs font-medium text-gray-500 uppercase w-12">#</th>
                <th className="px-4 py-2 text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="px-4 py-2 text-xs font-medium text-gray-500 uppercase text-right">Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {TOP_GIFTERS.map((user) => (
                <tr key={user.rank} className="hover:bg-gray-50">
                  <td className="px-4 py-2">
                    <span className={cn(
                      "inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium",
                      user.rank <= 3 ? "bg-yellow-100 text-yellow-700" : "bg-gray-100 text-gray-500"
                    )}>
                      {user.rank}
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    <p className="text-sm text-gray-900">@{user.username}</p>
                    <p className="text-xs text-gray-500">{user.count} gifts</p>
                  </td>
                  <td className="px-4 py-2 text-sm font-medium text-gray-900 text-right">
                    ${user.value?.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
