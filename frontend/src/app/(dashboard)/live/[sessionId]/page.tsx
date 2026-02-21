"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Eye, Gift, MessageCircle, Heart, UserPlus, Radio, BarChart3 } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";

interface LiveEvent {
  id: string;
  type: "comment" | "gift" | "like" | "follow" | "join" | "share";
  username: string;
  content: string;
  timestamp: string;
}

const TYPE_MAP: Record<string, StatusVariant> = {
  comment: "active",
  gift: "warning",
  like: "syncing",
  follow: "completed",
  join: "draft",
  share: "paused",
};

const MOCK_EVENTS: LiveEvent[] = [
  { id: "e1", type: "comment", username: "user_fan_1", content: "Love this product!", timestamp: "2026-02-20T10:45:12Z" },
  { id: "e2", type: "gift", username: "big_supporter", content: "Sent Rose x5", timestamp: "2026-02-20T10:45:08Z" },
  { id: "e3", type: "like", username: "viewer_42", content: "Liked the stream", timestamp: "2026-02-20T10:45:05Z" },
  { id: "e4", type: "follow", username: "new_follower", content: "Started following", timestamp: "2026-02-20T10:44:58Z" },
  { id: "e5", type: "comment", username: "shopper_tt", content: "How much is this?", timestamp: "2026-02-20T10:44:52Z" },
  { id: "e6", type: "gift", username: "vip_viewer", content: "Sent Galaxy x1", timestamp: "2026-02-20T10:44:45Z" },
  { id: "e7", type: "join", username: "curious_viewer", content: "Joined the stream", timestamp: "2026-02-20T10:44:40Z" },
  { id: "e8", type: "comment", username: "beauty_fan", content: "Can you show the shade options?", timestamp: "2026-02-20T10:44:35Z" },
  { id: "e9", type: "like", username: "happy_watcher", content: "Liked the stream", timestamp: "2026-02-20T10:44:30Z" },
  { id: "e10", type: "share", username: "sharer_99", content: "Shared to friends", timestamp: "2026-02-20T10:44:25Z" },
  { id: "e11", type: "comment", username: "deal_hunter", content: "Will there be a discount?", timestamp: "2026-02-20T10:44:20Z" },
  { id: "e12", type: "gift", username: "generous_one", content: "Sent Lion x2", timestamp: "2026-02-20T10:44:15Z" },
  { id: "e13", type: "follow", username: "newbie_tiktok", content: "Started following", timestamp: "2026-02-20T10:44:10Z" },
  { id: "e14", type: "comment", username: "first_timer", content: "First time here, love the vibe!", timestamp: "2026-02-20T10:44:05Z" },
  { id: "e15", type: "like", username: "silent_viewer", content: "Liked the stream", timestamp: "2026-02-20T10:44:00Z" },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export default function LiveSessionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;
  const [events] = useState<LiveEvent[]>(MOCK_EVENTS);

  const stats = {
    viewers: 12_400,
    gifts: 342,
    comments: events.filter((e) => e.type === "comment").length,
    likes: events.filter((e) => e.type === "like").length,
  };

  const columns: Column<LiveEvent>[] = [
    {
      key: "type",
      header: "Type",
      className: "w-28",
      render: (row) => <StatusBadge variant={TYPE_MAP[row.type] || "draft"} label={row.type} />,
    },
    {
      key: "user",
      header: "User",
      render: (row) => <span className="text-sm font-medium text-gray-900">@{row.username}</span>,
    },
    {
      key: "content",
      header: "Content",
      render: (row) => <span className="text-sm text-gray-600">{row.content}</span>,
    },
    {
      key: "time",
      header: "Time",
      className: "w-28",
      render: (row) => <span className="text-xs text-gray-400">{new Date(row.timestamp).toLocaleTimeString()}</span>,
    },
  ];

  return (
    <PageShell
      header={
        <>
          <div className="flex items-center justify-between mb-4">
            <button onClick={() => router.back()} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700">
              <ArrowLeft className="h-4 w-4" /> Back
            </button>
            <Link href={`/live/${sessionId}/analytics`} className="flex items-center gap-1.5 rounded-lg bg-gray-900 px-3 py-2 text-sm font-medium text-white hover:bg-gray-800 transition-colors">
              <BarChart3 className="h-4 w-4" /> View Analytics
            </Link>
          </div>
          <MetricBar>
            <MetricCard label="Viewers" value={formatNumber(stats.viewers)} icon={Eye} />
            <MetricCard label="Gifts" value={formatNumber(stats.gifts)} icon={Gift} />
            <MetricCard label="Comments" value={stats.comments} icon={MessageCircle} />
            <MetricCard label="Likes" value={stats.likes} icon={Heart} />
          </MetricBar>
        </>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Live feed" description="Events are captured in real-time from the LIVE stream. Comments dominate the engagement." variant="success" />
          <InsightItem title="Session" description={`Session: ${sessionId}`} />
        </InsightPanel>
      }
    >
      <div className="flex items-center gap-2 mb-4">
        <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
        <span className="text-sm font-medium text-gray-900">Live Event Feed</span>
      </div>

      <DataTable
        columns={columns}
        data={events}
        keyExtractor={(row) => row.id}
        emptyTitle="No events yet"
        emptyDescription="Events will appear here as they happen"
      />
    </PageShell>
  );
}
