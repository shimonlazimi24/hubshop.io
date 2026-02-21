"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Eye, Heart, MessageCircle, Share2 } from "lucide-react";
import { getVideo, getVideoMetrics, type VideoDetail, type VideoMetrics } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";

export default function VideoDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [video, setVideo] = useState<VideoDetail | null>(null);
  const [metrics, setMetrics] = useState<VideoMetrics[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAccessToken();
    if (!token || !id) return;

    Promise.all([
      getVideo(id, token),
      getVideoMetrics(id, token).catch(() => []),
    ])
      .then(([v, m]) => {
        setVideo(v);
        setMetrics(m);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-center py-8 text-gray-500">Loading...</div>;
  if (!video) return <div className="text-center py-8 text-gray-500">Video not found</div>;

  const viewsData = metrics.map((m) => m.views);

  return (
    <div>
      <Link href="/content" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4 transition-colors">
        <ArrowLeft className="h-4 w-4" /> Back to Videos
      </Link>

      <PageShell
        header={
          <MetricBar>
            <MetricCard
              label="Views"
              value={video.view_count.toLocaleString()}
              icon={Eye}
              iconColor="text-cyan"
              sparklineData={viewsData.length > 1 ? viewsData : undefined}
            />
            <MetricCard
              label="Likes"
              value={video.like_count.toLocaleString()}
              icon={Heart}
              iconColor="text-coral"
            />
            <MetricCard
              label="Comments"
              value={video.comment_count.toLocaleString()}
              icon={MessageCircle}
              iconColor="text-purple"
            />
            <MetricCard
              label="Shares"
              value={video.share_count.toLocaleString()}
              icon={Share2}
              iconColor="text-info"
            />
          </MetricBar>
        }
      >
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Video preview */}
          <div className="lg:col-span-2">
            <div className="rounded-xl border border-gray-100 bg-white overflow-hidden shadow-[var(--shadow-card)]">
              <div className="aspect-video bg-gray-900 flex items-center justify-center">
                {video.cover_url ? (
                  <img src={video.cover_url} alt={video.title || ""} className="max-h-full" />
                ) : (
                  <span className="text-gray-500">No preview available</span>
                )}
              </div>
              <div className="p-5">
                <h2 className="text-lg font-semibold text-gray-900">{video.title || "Untitled"}</h2>
                {video.description && (
                  <p className="text-sm text-gray-600 mt-2">{video.description}</p>
                )}
                <div className="flex items-center gap-2 mt-3">
                  <StatusBadge
                    variant={video.status === "PUBLIC" ? "active" : video.status === "PRIVATE" ? "paused" : "draft"}
                    label={video.status}
                  />
                  {video.duration && (
                    <span className="text-xs text-gray-400">
                      {Math.floor(video.duration / 60)}:{String(video.duration % 60).padStart(2, "0")}
                    </span>
                  )}
                  {video.create_time && (
                    <span className="text-xs text-gray-400">
                      Published {new Date(video.create_time).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Daily Metrics sidebar */}
          <div>
            {metrics.length > 0 && (
              <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-[var(--shadow-card)]">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Daily Metrics</h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {metrics.map((m) => (
                    <div key={m.id} className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">{m.date}</span>
                      <span className="text-gray-900 font-medium tabular-nums">{m.views.toLocaleString()} views</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </PageShell>
    </div>
  );
}
