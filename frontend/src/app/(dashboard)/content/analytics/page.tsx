"use client";

import { useEffect, useState } from "react";
import { Eye, Heart, MessageCircle, Share2 } from "lucide-react";
import { listVideos, type VideoSummary, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

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

  const topVideos = [...videos].sort((a, b) => b.view_count - a.view_count).slice(0, 5);

  const kpis = [
    { label: "Total Views", value: totalViews, icon: Eye },
    { label: "Total Likes", value: totalLikes, icon: Heart },
    { label: "Total Comments", value: totalComments, icon: MessageCircle },
    { label: "Total Shares", value: totalShares, icon: Share2 },
  ];

  if (loading) return <div className="text-center py-8 text-gray-500">Loading analytics...</div>;

  return (
    <div className="max-w-5xl">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div key={kpi.label} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center gap-2 mb-2">
                <Icon className="h-4 w-4 text-gray-400" />
                <span className="text-xs text-gray-500">{kpi.label}</span>
              </div>
              <p className="text-2xl font-semibold text-gray-900">{kpi.value.toLocaleString()}</p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Engagement Rate</h3>
          <p className="text-3xl font-semibold text-gray-900">{avgEngagement}%</p>
          <p className="text-xs text-gray-500 mt-1">Average across {videos.length} videos</p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Top Videos by Views</h3>
          <div className="space-y-2">
            {topVideos.map((v, i) => (
              <div key={v.id} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 truncate flex-1">
                  <span className="text-gray-400 mr-2">#{i + 1}</span>
                  {v.title || "Untitled"}
                </span>
                <span className="text-sm font-medium text-gray-900 ml-2">{v.view_count.toLocaleString()}</span>
              </div>
            ))}
            {topVideos.length === 0 && <p className="text-sm text-gray-500">No videos yet</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
