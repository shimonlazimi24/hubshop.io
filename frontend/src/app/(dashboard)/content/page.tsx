"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Eye, Heart, Users, RefreshCw, TrendingUp, ArrowRight } from "lucide-react";
import { listVideos, syncVideos, type VideoSummary, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { CreativeCard } from "@/components/ui/creative-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { EmptyState } from "@/components/ui/empty-state";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { toast } from "@/lib/toast-store";
import { useWorkspace } from "@/hooks/useWorkspace";


function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export default function VideosPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const [data, setData] = useState<PaginatedResponse<VideoSummary> | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);

  const token = getAccessToken();

  useEffect(() => {
    loadVideos();
  }, [search, statusFilter, page]);

  function loadVideos() {
    if (!token || !WORKSPACE_ID) return;
    setLoading(true);
    listVideos(WORKSPACE_ID, token, {
      search: search || undefined,
      status_filter: statusFilter || undefined,
      page,
    })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleSync() {
    if (!token || !WORKSPACE_ID) return;
    setSyncing(true);
    try {
      await syncVideos(WORKSPACE_ID, token);
      toast.success("Videos synced successfully");
      loadVideos();
    } catch {
      toast.error("Failed to sync videos");
    } finally {
      setSyncing(false);
    }
  }

  const videos = data?.items ?? [];
  const totalViews = videos.reduce((s, v) => s + v.view_count, 0);
  const totalLikes = videos.reduce((s, v) => s + v.like_count, 0);
  const avgEngagement = videos.length > 0
    ? ((totalLikes + videos.reduce((s, v) => s + v.comment_count + v.share_count, 0)) / (totalViews || 1) * 100)
    : 0;

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
            label="Engagement Rate"
            value={`${avgEngagement.toFixed(1)}%`}
            icon={Heart}
            iconColor="text-coral"
            trend={{ value: 2.3, direction: "up", label: "vs last week" }}
            sparklineData={[4.2, 4.5, 4.3, 4.6, 4.8, 4.7, 5.0]}
            loading={loading}
          />
          <MetricCard
            label="Followers"
            value="84.5K"
            icon={Users}
            iconColor="text-purple"
            trend={{ value: 1.8, direction: "up", label: "vs last week" }}
            sparklineData={[80, 81, 82, 82.5, 83, 83.8, 84.5]}
            loading={loading}
          />
          <MetricCard
            label="Publishing Rate"
            value={`${videos.length} videos`}
            icon={TrendingUp}
            iconColor="text-success"
            trend={{ value: 0, direction: "flat" }}
            loading={loading}
          />
        </MetricBar>
      }
      aside={
        <InsightPanel defaultOpen={false}>
          <InsightItem
            icon={<TrendingUp className="h-4 w-4 text-success" />}
            title="Top performer"
            description="Your most viewed video this week has 48K views. Consider boosting it with a Spark Ad."
            variant="success"
            action={{ label: "View video", onClick: () => {} }}
          />
          <InsightItem
            icon={<Eye className="h-4 w-4 text-info" />}
            title="Best posting time"
            description="Videos posted between 6-8 PM get 32% more engagement on average."
            variant="default"
          />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={(v) => { setSearch(v); setPage(1); }}
        searchPlaceholder="Search videos..."
        actions={
          <button
            onClick={handleSync}
            disabled={syncing}
            className="inline-flex items-center gap-1.5 rounded-lg bg-coral px-4 py-2 text-sm font-medium text-white hover:bg-coral-dark transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${syncing ? "animate-spin" : ""}`} />
            {syncing ? "Syncing..." : "Sync Videos"}
          </button>
        }
      >
        <FilterDropdown
          label="All Statuses"
          value={statusFilter}
          options={[
            { label: "Public", value: "PUBLIC" },
            { label: "Private", value: "PRIVATE" },
            { label: "Friends Only", value: "FRIEND" },
          ]}
          onChange={(v) => { setStatusFilter(v); setPage(1); }}
        />
      </FilterBar>

      {/* "View all in Creative Hub" link */}
      <div className="mb-4">
        <Link
          href="/creatives"
          className="inline-flex items-center gap-1 text-sm font-medium text-coral hover:text-coral-dark transition-colors"
        >
          View all in Creative Hub <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      {/* Video grid using CreativeCard */}
      {!loading && videos.length === 0 ? (
        <EmptyState
          title="No videos found"
          description="Sync your videos from TikTok to get started."
          action={{ label: "Sync Videos", onClick: handleSync }}
        />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {videos.map((video) => (
            <CreativeCard
              key={video.id}
              title={video.title || "Untitled"}
              thumbnailUrl={video.cover_url || undefined}
              format="video"
              metrics={[
                { label: "Views", value: formatNumber(video.view_count) },
                { label: "Likes", value: formatNumber(video.like_count) },
                { label: "Comments", value: formatNumber(video.comment_count) },
              ]}
              onClick={() => { window.location.href = `/content/videos/${video.id}`; }}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-xs text-gray-500">
            Page {data.page} of {data.total_pages} ({data.total} total)
          </p>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
              disabled={page >= data.total_pages}
              className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {loading && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="rounded-xl border border-gray-100 bg-white overflow-hidden">
              <div className="aspect-[9/16] max-h-48 bg-gray-100 animate-pulse" />
              <div className="p-3 space-y-2">
                <div className="h-4 w-24 rounded bg-gray-100 animate-pulse" />
                <div className="h-3 w-16 rounded bg-gray-100 animate-pulse" />
              </div>
            </div>
          ))}
        </div>
      )}
    </PageShell>
  );
}
