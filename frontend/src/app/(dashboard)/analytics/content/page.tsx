"use client";

import { useEffect, useState } from "react";
import { Eye, Users, Heart, Video, MessageCircle } from "lucide-react";
import { getContentPerformance, getTopPerformers, getAnalyticsOverview } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { toast } from "@/lib/toast-store";
import { Skeleton } from "@/components/ui/skeleton";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

interface PerfRow {
  date: string;
  views: number;
  likes: number;
  shares: number;
}

interface VideoRow {
  title: string;
  views: number;
  likes: number;
  comments: number;
}

export default function ContentAnalyticsPage() {
  const [overview, setOverview] = useState<{ total_video_views: number; total_followers: number } | null>(null);
  const [performance, setPerformance] = useState<PerfRow[]>([]);
  const [topVideos, setTopVideos] = useState<VideoRow[]>([]);
  const [loading, setLoading] = useState(true);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    Promise.all([
      getAnalyticsOverview(WORKSPACE_ID, token, 30),
      getContentPerformance(WORKSPACE_ID, token),
      getTopPerformers(WORKSPACE_ID, token, 10),
    ])
      .then(([ov, perf, performers]) => {
        setOverview({ total_video_views: ov.total_video_views, total_followers: ov.total_followers });
        setPerformance(
          (perf || []).map((d: Record<string, unknown>, i: number) => ({
            date: (d.date as string) || `Day ${i + 1}`,
            views: (d.views as number) || 0,
            likes: (d.likes as number) || 0,
            shares: (d.shares as number) || 0,
          }))
        );
        setTopVideos(
          (performers.top_videos || []).map((v: Record<string, unknown>, i: number) => ({
            title: (v.title as string) || `Video ${i + 1}`,
            views: (v.views as number) || 0,
            likes: (v.likes as number) || 0,
            comments: (v.comments as number) || 0,
          }))
        );
      })
      .catch(() => toast.error("Failed to load content analytics"))
      .finally(() => setLoading(false));
  }, []);

  function formatNumber(n: number): string {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
    return n.toLocaleString();
  }

  const videoColumns: Column<VideoRow>[] = [
    {
      key: "title",
      header: "Title",
      render: (row) => <span className="text-sm font-medium text-gray-900 truncate max-w-xs block">{row.title}</span>,
    },
    {
      key: "views",
      header: "Views",
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{formatNumber(row.views)}</span>,
    },
    {
      key: "likes",
      header: "Likes",
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{formatNumber(row.likes)}</span>,
    },
    {
      key: "comments",
      header: "Comments",
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{formatNumber(row.comments)}</span>,
    },
  ];

  return (
    <PageShell
      header={
        loading ? (
          <MetricBar>
            <Skeleton className="h-16 flex-1 rounded-xl" />
            <Skeleton className="h-16 flex-1 rounded-xl" />
          </MetricBar>
        ) : (
          <MetricBar>
            <MetricCard label="Total Video Views (30d)" value={formatNumber(overview?.total_video_views || 0)} icon={Eye} />
            <MetricCard label="Total Followers" value={formatNumber(overview?.total_followers || 0)} icon={Users} />
          </MetricBar>
        )
      }
      aside={
        <InsightPanel>
          <InsightItem
            title="Content performance"
            description={overview ? `${formatNumber(overview.total_video_views)} views in the last 30 days across all content.` : "Loading..."}
            variant="success"
          />
          <InsightItem
            title="Engagement"
            description="Top videos are ranked by total views. Check likes and comments for engagement quality."
          />
        </InsightPanel>
      }
    >
      {/* Content Performance */}
      <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] mb-6">
        <div className="px-4 py-3 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-900">Content Performance</h3>
        </div>
        <div className="p-4">
          {performance.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {performance.map((d, i) => (
                <div key={i} className="flex items-center gap-4 text-sm">
                  <span className="text-gray-500 w-24">
                    {d.date.startsWith("Day") ? d.date : new Date(d.date).toLocaleDateString()}
                  </span>
                  <div className="flex-1 grid grid-cols-3 gap-4">
                    <div className="flex items-center gap-1.5">
                      <Eye className="h-3 w-3 text-gray-400" />
                      <span className="text-gray-600 tabular-nums">{formatNumber(d.views)}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Heart className="h-3 w-3 text-gray-400" />
                      <span className="text-gray-600 tabular-nums">{formatNumber(d.likes)}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <MessageCircle className="h-3 w-3 text-gray-400" />
                      <span className="text-gray-600 tabular-nums">{formatNumber(d.shares)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-400 py-8">No performance data</p>
          )}
        </div>
      </div>

      {/* Top Videos */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Video className="h-4 w-4 text-cyan-500" />
          <h3 className="text-sm font-semibold text-gray-900">Top Videos</h3>
        </div>
        <DataTable
          columns={videoColumns}
          data={topVideos}
          keyExtractor={(row) => row.title}
          emptyTitle="No video data"
          emptyDescription="Video performance data will appear here"
        />
      </div>
    </PageShell>
  );
}
