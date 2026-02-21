"use client";

import { useState } from "react";
import Link from "next/link";
import { Clock, Eye, Gift, DollarSign } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { ActionMenu } from "@/components/ui/action-menu";

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
  { id: "hist-1", streamer_username: "beauty_live", streamer_display_name: "Beauty LIVE", date: "2026-02-20T09:30:00Z", duration_minutes: 120, total_viewers: 34_500, peak_viewers: 12_400, gift_revenue: 2_890.50, total_comments: 4_560 },
  { id: "hist-2", streamer_username: "shop_showcase", streamer_display_name: "Shop Showcase", date: "2026-02-19T14:00:00Z", duration_minutes: 90, total_viewers: 22_100, peak_viewers: 8_900, gift_revenue: 1_450.00, total_comments: 2_890 },
  { id: "hist-3", streamer_username: "gaming_tt", streamer_display_name: "GameTime", date: "2026-02-18T20:00:00Z", duration_minutes: 240, total_viewers: 67_800, peak_viewers: 28_900, gift_revenue: 5_670.00, total_comments: 12_340 },
  { id: "hist-4", streamer_username: "cooking_live", streamer_display_name: "Cook With Us", date: "2026-02-17T11:00:00Z", duration_minutes: 60, total_viewers: 15_200, peak_viewers: 6_700, gift_revenue: 890.00, total_comments: 1_780 },
  { id: "hist-5", streamer_username: "music_live_show", streamer_display_name: "Music Live", date: "2026-02-16T19:00:00Z", duration_minutes: 150, total_viewers: 45_600, peak_viewers: 18_200, gift_revenue: 3_450.00, total_comments: 8_900 },
  { id: "hist-6", streamer_username: "fitness_stream", streamer_display_name: "FitLive", date: "2026-02-15T07:00:00Z", duration_minutes: 45, total_viewers: 8_900, peak_viewers: 3_200, gift_revenue: 340.00, total_comments: 567 },
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
  const [search, setSearch] = useState("");

  const filtered = history.filter((s) => !search || s.streamer_display_name.toLowerCase().includes(search.toLowerCase()));
  const totalRevenue = history.reduce((sum, s) => sum + s.gift_revenue, 0);
  const avgViewers = Math.round(history.reduce((sum, s) => sum + s.total_viewers, 0) / history.length);

  const columns: Column<PastSession>[] = [
    {
      key: "streamer",
      header: "Streamer",
      render: (row) => (
        <div>
          <p className="text-sm font-medium text-gray-900">{row.streamer_display_name}</p>
          <p className="text-xs text-gray-500">@{row.streamer_username}</p>
        </div>
      ),
    },
    {
      key: "date",
      header: "Date",
      render: (row) => <span className="text-sm text-gray-600">{new Date(row.date).toLocaleDateString()}</span>,
    },
    {
      key: "duration",
      header: "Duration",
      render: (row) => (
        <div className="flex items-center gap-1.5"><Clock className="h-3.5 w-3.5 text-gray-400" /><span className="text-sm text-gray-600">{formatDuration(row.duration_minutes)}</span></div>
      ),
    },
    {
      key: "viewers",
      header: "Total Viewers",
      render: (row) => (
        <div className="flex items-center gap-1.5"><Eye className="h-3.5 w-3.5 text-gray-400" /><span className="text-sm text-gray-600">{formatNumber(row.total_viewers)}</span></div>
      ),
    },
    {
      key: "revenue",
      header: "Gift Revenue",
      render: (row) => (
        <div className="flex items-center gap-1.5"><DollarSign className="h-3.5 w-3.5 text-green-500" /><span className="text-sm font-medium text-gray-900">${row.gift_revenue.toLocaleString()}</span></div>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      className: "w-24",
      render: (row) => (
        <ActionMenu items={[
          { label: "View Analytics", onClick: () => window.location.href = `/live/${row.id}/analytics` },
          { label: "View Events", onClick: () => window.location.href = `/live/${row.id}` },
        ]} />
      ),
    },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Total Sessions" value={history.length} icon={Clock} />
          <MetricCard label="Avg Viewers" value={formatNumber(avgViewers)} icon={Eye} />
          <MetricCard label="Total Revenue" value={`$${totalRevenue.toLocaleString()}`} icon={DollarSign} trend={{ value: 15, direction: "up" }} />
          <MetricCard label="Total Gifts" value={formatNumber(history.reduce((s, h) => s + Math.round(h.gift_revenue / 5), 0))} icon={Gift} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Top session" description="GameTime generated $5,670 in gifts over 4 hours. Long-form LIVE streams drive more gifting." variant="success" />
          <InsightItem title="Revenue trend" description="Gift revenue is up 15% compared to the previous period." variant="success" />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search past sessions..."
      />

      <DataTable
        columns={columns}
        data={filtered}
        keyExtractor={(row) => row.id}
        emptyTitle="No past sessions"
        emptyDescription="Session history will appear here after monitoring ends"
      />
    </PageShell>
  );
}
