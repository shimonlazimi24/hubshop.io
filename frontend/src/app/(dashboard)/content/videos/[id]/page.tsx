"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Eye, Heart, MessageCircle, Share2 } from "lucide-react";
import { getVideo, getVideoMetrics, type VideoDetail, type VideoMetrics } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

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

  const stats = [
    { label: "Views", value: video.view_count, icon: Eye },
    { label: "Likes", value: video.like_count, icon: Heart },
    { label: "Comments", value: video.comment_count, icon: MessageCircle },
    { label: "Shares", value: video.share_count, icon: Share2 },
  ];

  return (
    <div>
      <Link href="/content" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4">
        <ArrowLeft className="h-4 w-4" /> Back to Videos
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="aspect-video bg-gray-900 flex items-center justify-center">
              {video.cover_url ? (
                <img src={video.cover_url} alt={video.title || ""} className="max-h-full" />
              ) : (
                <span className="text-gray-500">No preview available</span>
              )}
            </div>
            <div className="p-4">
              <h2 className="text-lg font-semibold text-gray-900">{video.title || "Untitled"}</h2>
              {video.description && (
                <p className="text-sm text-gray-600 mt-2">{video.description}</p>
              )}
              <div className="flex items-center gap-2 mt-3">
                <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-800">{video.status}</span>
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

        <div className="space-y-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Performance</h3>
            <div className="grid grid-cols-2 gap-3">
              {stats.map((s) => {
                const Icon = s.icon;
                return (
                  <div key={s.label} className="text-center p-3 rounded-lg bg-gray-50">
                    <Icon className="h-4 w-4 text-gray-400 mx-auto mb-1" />
                    <p className="text-lg font-semibold text-gray-900">{s.value.toLocaleString()}</p>
                    <p className="text-xs text-gray-500">{s.label}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {metrics.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Daily Metrics</h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {metrics.map((m) => (
                  <div key={m.id} className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">{m.date}</span>
                    <span className="text-gray-900">{m.views.toLocaleString()} views</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
