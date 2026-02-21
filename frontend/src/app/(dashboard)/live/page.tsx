"use client";

import { useState } from "react";
import Link from "next/link";
import { Radio, Eye, Gift, MessageCircle, Clock } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";

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

const STATUS_MAP: Record<string, StatusVariant> = {
  monitoring: "active",
  ended: "completed",
  error: "error",
};

const MOCK_SESSIONS: LiveSession[] = [
  { id: "sess-1", streamer_username: "beauty_live", streamer_display_name: "Beauty LIVE", status: "monitoring", viewer_count: 12_400, gift_count: 342, comment_count: 1_890, started_at: "2026-02-20T09:30:00Z", duration_minutes: 45 },
  { id: "sess-2", streamer_username: "shop_showcase", streamer_display_name: "Shop Showcase", status: "monitoring", viewer_count: 8_900, gift_count: 156, comment_count: 987, started_at: "2026-02-20T10:00:00Z", duration_minutes: 15 },
  { id: "sess-3", streamer_username: "gaming_tt", streamer_display_name: "GameTime", status: "ended", viewer_count: 34_500, gift_count: 892, comment_count: 4_560, started_at: "2026-02-20T06:00:00Z", duration_minutes: 180 },
  { id: "sess-4", streamer_username: "music_live_show", streamer_display_name: "Music Live", status: "error", viewer_count: 0, gift_count: 0, comment_count: 0, started_at: "2026-02-20T08:00:00Z", duration_minutes: 2 },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export default function LiveOverviewPage() {
  const [sessions] = useState<LiveSession[]>(MOCK_SESSIONS);
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");

  const filtered = sessions.filter((s) => {
    if (statusFilter && s.status !== statusFilter) return false;
    if (search && !s.streamer_display_name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const activeCount = sessions.filter((s) => s.status === "monitoring").length;
  const totalViewers = sessions.reduce((sum, s) => sum + s.viewer_count, 0);
  const totalGifts = sessions.reduce((sum, s) => sum + s.gift_count, 0);

  const columns: Column<LiveSession>[] = [
    {
      key: "streamer",
      header: "Streamer",
      render: (row) => (
        <Link href={`/live/${row.id}`} className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
            <Radio className={`h-5 w-5 ${row.status === "monitoring" ? "text-coral" : "text-gray-400"}`} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900 group-hover:text-coral transition-colors">{row.streamer_display_name}</p>
            <p className="text-xs text-gray-500">@{row.streamer_username}</p>
          </div>
        </Link>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (row) => <StatusBadge variant={STATUS_MAP[row.status] || "draft"} label={row.status} />,
    },
    {
      key: "viewers",
      header: "Viewers",
      render: (row) => (
        <div className="flex items-center gap-1.5"><Eye className="h-3.5 w-3.5 text-gray-400" /><span className="text-sm text-gray-600">{formatNumber(row.viewer_count)}</span></div>
      ),
    },
    {
      key: "gifts",
      header: "Gifts",
      render: (row) => (
        <div className="flex items-center gap-1.5"><Gift className="h-3.5 w-3.5 text-gray-400" /><span className="text-sm text-gray-600">{formatNumber(row.gift_count)}</span></div>
      ),
    },
    {
      key: "comments",
      header: "Comments",
      render: (row) => (
        <div className="flex items-center gap-1.5"><MessageCircle className="h-3.5 w-3.5 text-gray-400" /><span className="text-sm text-gray-600">{formatNumber(row.comment_count)}</span></div>
      ),
    },
    {
      key: "duration",
      header: "Duration",
      render: (row) => (
        <div className="flex items-center gap-1.5"><Clock className="h-3.5 w-3.5 text-gray-400" /><span className="text-sm text-gray-500">{row.duration_minutes}m</span></div>
      ),
    },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Active Streams" value={activeCount} icon={Radio} trend={{ value: activeCount, direction: activeCount > 0 ? "up" : "flat" }} />
          <MetricCard label="Total Viewers" value={formatNumber(totalViewers)} icon={Eye} />
          <MetricCard label="Total Gifts" value={formatNumber(totalGifts)} icon={Gift} />
          <MetricCard label="Total Sessions" value={sessions.length} icon={Clock} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Live now" description={`${activeCount} stream${activeCount !== 1 ? "s" : ""} currently being monitored. Real-time events are being captured.`} variant={activeCount > 0 ? "success" : "default"} />
          <InsightItem title="Error detected" description="Music Live session encountered an error. Check connection and retry." variant="warning" />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search streams..."
        actions={
          <Link href="/live/monitor" className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 transition-colors">
            Monitor Stream
          </Link>
        }
      >
        <FilterDropdown
          label="Status"
          value={statusFilter}
          onChange={setStatusFilter}
          options={[
            { label: "Monitoring", value: "monitoring" },
            { label: "Ended", value: "ended" },
            { label: "Error", value: "error" },
          ]}
        />
      </FilterBar>

      <DataTable
        columns={columns}
        data={filtered}
        keyExtractor={(row) => row.id}
        emptyTitle="No monitoring sessions"
        emptyDescription="Start monitoring a LIVE stream to see events in real-time"
        emptyAction={{ label: "Monitor Stream", onClick: () => window.location.href = "/live/monitor" }}
      />
    </PageShell>
  );
}
