"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Eye, Users, Gift, TrendingUp, MessageCircle, DollarSign } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
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

  const commenterColumns: Column<TopContributor>[] = [
    {
      key: "rank",
      header: "#",
      className: "w-12",
      render: (row) => (
        <span className={cn("inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium", row.rank <= 3 ? "bg-coral/10 text-coral" : "bg-gray-100 text-gray-500")}>
          {row.rank}
        </span>
      ),
    },
    {
      key: "user",
      header: "User",
      render: (row) => <span className="text-sm text-gray-900">@{row.username}</span>,
    },
    {
      key: "count",
      header: "Comments",
      render: (row) => <span className="text-sm text-gray-600 text-right tabular-nums">{row.count}</span>,
    },
  ];

  const gifterColumns: Column<TopContributor>[] = [
    {
      key: "rank",
      header: "#",
      className: "w-12",
      render: (row) => (
        <span className={cn("inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium", row.rank <= 3 ? "bg-yellow-100 text-yellow-700" : "bg-gray-100 text-gray-500")}>
          {row.rank}
        </span>
      ),
    },
    {
      key: "user",
      header: "User",
      render: (row) => (
        <div>
          <p className="text-sm text-gray-900">@{row.username}</p>
          <p className="text-xs text-gray-500">{row.count} gifts</p>
        </div>
      ),
    },
    {
      key: "value",
      header: "Value",
      render: (row) => <span className="text-sm font-medium text-gray-900 tabular-nums">${row.value?.toFixed(2)}</span>,
    },
  ];

  return (
    <PageShell
      header={
        <>
          <button onClick={() => router.back()} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-4">
            <ArrowLeft className="h-4 w-4" /> Back to Event Feed
          </button>
          <div className="flex items-center gap-2 mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Post-Stream Analytics</h2>
            <span className="text-sm text-gray-400">Session: {sessionId}</span>
          </div>
          <MetricBar>
            <MetricCard label="Total Viewers" value={formatNumber(MOCK_KPI.total_viewers)} icon={Eye} />
            <MetricCard label="Peak Concurrent" value={formatNumber(MOCK_KPI.peak_concurrent)} icon={Users} />
            <MetricCard label="Gift Revenue" value={`$${MOCK_KPI.gift_revenue.toLocaleString()}`} icon={DollarSign} />
            <MetricCard label="Engagement Rate" value={`${MOCK_KPI.engagement_rate}%`} icon={TrendingUp} trend={{ value: MOCK_KPI.engagement_rate, direction: MOCK_KPI.engagement_rate > 5 ? "up" : "flat" }} />
          </MetricBar>
        </>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Strong engagement" description={`${MOCK_KPI.engagement_rate}% engagement rate is well above the 3-5% average for LIVE streams.`} variant="success" />
          <InsightItem title="Gift revenue" description={`$${MOCK_KPI.gift_revenue.toLocaleString()} earned. Top gifter contributed $890 (31% of total).`} />
          <InsightItem title="Duration impact" description={`${MOCK_KPI.duration_minutes} minute session. Longer sessions (2h+) correlate with higher gift revenue.`} />
        </InsightPanel>
      }
    >
      {/* Additional Stats */}
      <div className="grid grid-cols-4 gap-3 mb-6">
        <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-3 text-center">
          <p className="text-sm font-semibold text-gray-900">{formatNumber(MOCK_KPI.total_comments)}</p>
          <p className="text-xs text-gray-500">Comments</p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-3 text-center">
          <p className="text-sm font-semibold text-gray-900">{formatNumber(MOCK_KPI.total_likes)}</p>
          <p className="text-xs text-gray-500">Likes</p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-3 text-center">
          <p className="text-sm font-semibold text-gray-900">{formatNumber(MOCK_KPI.total_shares)}</p>
          <p className="text-xs text-gray-500">Shares</p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-3 text-center">
          <p className="text-sm font-semibold text-gray-900">{MOCK_KPI.duration_minutes}m</p>
          <p className="text-xs text-gray-500">Duration</p>
        </div>
      </div>

      {/* Top Contributors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <MessageCircle className="h-4 w-4 text-blue-500" />
            <h3 className="text-sm font-semibold text-gray-900">Top Commenters</h3>
          </div>
          <DataTable columns={commenterColumns} data={TOP_COMMENTERS} keyExtractor={(row) => String(row.rank)} emptyTitle="No data" emptyDescription="" />
        </div>
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Gift className="h-4 w-4 text-yellow-500" />
            <h3 className="text-sm font-semibold text-gray-900">Top Gifters</h3>
          </div>
          <DataTable columns={gifterColumns} data={TOP_GIFTERS} keyExtractor={(row) => String(row.rank)} emptyTitle="No data" emptyDescription="" />
        </div>
      </div>
    </PageShell>
  );
}
