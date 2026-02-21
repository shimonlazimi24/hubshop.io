"use client";

import { useEffect, useState } from "react";
import { Eye, Heart, MessageCircle, Share2, TrendingUp } from "lucide-react";
import { listVideos, type VideoSummary, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { ChartCard } from "@/components/ui/chart-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

const topVideoColumns: Column<VideoSummary>[] = [
  {
    key: "rank",
    header: "#",
    className: "w-10",
    render: (_row, idx) => <span className="text-sm text-gray-400 font-medium">{idx + 1}</span>,
  },
  {
    key: "title",
    header: "Title",
    render: (row) => (
      <span className="text-sm text-gray-900 font-medium truncate block max-w-[300px]">
        {row.title || "Untitled"}
      </span>
    ),
  },
  {
    key: "views",
    header: "Views",
    sortable: true,
    render: (row) => <span className="text-sm text-gray-900 tabular-nums">{row.view_count.toLocaleString()}</span>,
  },
  {
    key: "likes",
    header: "Likes",
    sortable: true,
    render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.like_count.toLocaleString()}</span>,
  },
  {
    key: "comments",
    header: "Comments",
    render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.comment_count.toLocaleString()}</span>,
  },
];

export default function ContentAnalyticsPage() {
  const [videos, setVideos] = useState<VideoSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;
    listVideos(WORKSPACE_ID, token, { page_size: 50 })
      .then((data) => setVideos(data.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const totalViews = videos.reduce((s, v) => s + v.view_count, 0);
  const totalLikes = videos.reduce((s, v) => s + v.like_count, 0);
  const totalComments = videos.reduce((s, v) => s + v.comment_count, 0);
  const totalShares = videos.reduce((s, v) => s + v.share_count, 0);
  const avgEngagement = videos.length > 0
    ? ((totalLikes + totalComments + totalShares) / (totalViews || 1) * 100).toFixed(2)
    : "0";

  const topVideos = [...videos].sort((a, b) => b.view_count - a.view_count).slice(0, 10);

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Total Views"
            value={formatNumber(totalViews)}
            icon={Eye}
            iconColor="text-cyan"
            trend={{ value: 14.2, direction: "up", label: "vs last week" }}
            sparklineData={[400, 420, 450, 430, 460, 480, 500]}
            loading={loading}
          />
          <MetricCard
            label="Total Likes"
            value={formatNumber(totalLikes)}
            icon={Heart}
            iconColor="text-coral"
            trend={{ value: 8.5, direction: "up", label: "vs last week" }}
            sparklineData={[120, 130, 125, 140, 135, 145, 150]}
            loading={loading}
          />
          <MetricCard
            label="Total Comments"
            value={formatNumber(totalComments)}
            icon={MessageCircle}
            iconColor="text-purple"
            loading={loading}
          />
          <MetricCard
            label="Total Shares"
            value={formatNumber(totalShares)}
            icon={Share2}
            iconColor="text-info"
            loading={loading}
          />
        </MetricBar>
      }
      aside={
        <InsightPanel defaultOpen={false}>
          <InsightItem
            icon={<TrendingUp className="h-4 w-4 text-success" />}
            title="Engagement trending up"
            description={`Your average engagement rate is ${avgEngagement}%. This is 12% higher than last month.`}
            variant="success"
          />
          <InsightItem
            icon={<Eye className="h-4 w-4 text-info" />}
            title="Peak viewing hours"
            description="Your audience is most active between 6-9 PM EST. Schedule content accordingly."
            variant="default"
          />
        </InsightPanel>
      }
    >
      {/* Engagement rate card + chart placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <ChartCard title="Engagement Rate">
          <div className="flex flex-col items-center justify-center h-full">
            <p className="text-4xl font-bold text-gray-900">{avgEngagement}%</p>
            <p className="text-sm text-gray-500 mt-1">Average across {videos.length} videos</p>
          </div>
        </ChartCard>

        <ChartCard title="Views Over Time">
          <div className="flex items-end gap-1 h-full px-2">
            {/* Simple bar chart placeholder using top video data */}
            {topVideos.slice(0, 7).map((v, i) => {
              const maxViews = Math.max(...topVideos.slice(0, 7).map((x) => x.view_count), 1);
              const height = (v.view_count / maxViews) * 100;
              return (
                <div key={v.id} className="flex-1 group relative">
                  <div
                    className="bg-coral/80 rounded-t hover:bg-coral transition-colors"
                    style={{ height: `${Math.max(height, 4)}%` }}
                  />
                </div>
              );
            })}
          </div>
        </ChartCard>
      </div>

      {/* Top Videos Table */}
      <h3 className="text-sm font-semibold text-gray-900 mb-3">Top Videos by Views</h3>
      <DataTable
        columns={topVideoColumns}
        data={topVideos}
        keyExtractor={(row) => row.id}
        emptyTitle="No videos yet"
        emptyDescription="Sync your videos from TikTok to see analytics."
        loading={loading}
      />
    </PageShell>
  );
}
