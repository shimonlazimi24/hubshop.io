"use client";

import { useEffect, useState } from "react";
import { getContentPerformance, getTopPerformers, getAnalyticsOverview } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

export default function ContentAnalyticsPage() {
  const [overview, setOverview] = useState<{ total_video_views: number; total_followers: number } | null>(null);
  const [performance, setPerformance] = useState<Record<string, unknown>[]>([]);
  const [topVideos, setTopVideos] = useState<Record<string, unknown>[]>([]);
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
        setPerformance(perf);
        setTopVideos(performers.top_videos);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase">Total Video Views (30d)</p>
          <p className="text-2xl font-semibold text-gray-900 mt-1">{(overview?.total_video_views || 0).toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase">Total Followers</p>
          <p className="text-2xl font-semibold text-gray-900 mt-1">{(overview?.total_followers || 0).toLocaleString()}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 mb-6">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Content Performance</h3>
        </div>
        <div className="p-4">
          {performance.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {performance.map((d, i) => (
                <div key={i} className="flex items-center gap-4 text-sm">
                  <span className="text-gray-500 w-24">
                    {d.date ? new Date(d.date as string).toLocaleDateString() : `Day ${i + 1}`}
                  </span>
                  <div className="flex-1 grid grid-cols-3 gap-4">
                    <span className="text-gray-600">Views: {((d.views as number) || 0).toLocaleString()}</span>
                    <span className="text-gray-600">Likes: {((d.likes as number) || 0).toLocaleString()}</span>
                    <span className="text-gray-600">Shares: {((d.shares as number) || 0).toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">No performance data</p>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Top Videos</h3>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Title</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Views</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Likes</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Comments</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {topVideos.map((v, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900 truncate max-w-xs">{(v.title as string) || `Video ${i + 1}`}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{((v.views as number) || 0).toLocaleString()}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{((v.likes as number) || 0).toLocaleString()}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{((v.comments as number) || 0).toLocaleString()}</td>
              </tr>
            ))}
            {topVideos.length === 0 && (
              <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">No video data</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Loading content analytics...</div>}
    </div>
  );
}
