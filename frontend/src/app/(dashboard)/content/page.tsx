"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Eye, Heart, MessageCircle, Share2 } from "lucide-react";
import { listVideos, syncVideos, type VideoSummary, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_COLORS: Record<string, string> = {
  PUBLIC: "bg-green-100 text-green-800",
  PRIVATE: "bg-gray-100 text-gray-800",
  FRIEND: "bg-blue-100 text-blue-800",
};

export default function VideosPage() {
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
    if (!token) return;
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
    if (!token) return;
    setSyncing(true);
    try {
      const result = await syncVideos(WORKSPACE_ID, token);
      loadVideos();
    } catch (err) {
      console.error(err);
    } finally {
      setSyncing(false);
    }
  }

  function formatNumber(n: number): string {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
    return String(n);
  }

  return (
    <div>
      <div className="flex items-center gap-4 mb-4">
        <input
          type="text"
          placeholder="Search videos..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm w-64"
        />
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm"
        >
          <option value="">All Statuses</option>
          <option value="PUBLIC">Public</option>
          <option value="PRIVATE">Private</option>
          <option value="FRIEND">Friends Only</option>
        </select>
        <div className="flex-1" />
        <button
          onClick={handleSync}
          disabled={syncing}
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {syncing ? "Syncing..." : "Sync Videos"}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data?.items.map((video) => (
          <Link
            key={video.id}
            href={`/content/videos/${video.id}`}
            className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
          >
            <div className="aspect-video bg-gray-100 relative">
              {video.cover_url ? (
                <img src={video.cover_url} alt={video.title || ""} className="w-full h-full object-cover" />
              ) : (
                <div className="flex items-center justify-center h-full text-gray-300 text-sm">No thumbnail</div>
              )}
              {video.duration && (
                <span className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-1.5 py-0.5 rounded">
                  {Math.floor(video.duration / 60)}:{String(video.duration % 60).padStart(2, "0")}
                </span>
              )}
            </div>
            <div className="p-3">
              <h3 className="text-sm font-medium text-gray-900 truncate">
                {video.title || "Untitled"}
              </h3>
              <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                <span className="flex items-center gap-1"><Eye className="h-3 w-3" />{formatNumber(video.view_count)}</span>
                <span className="flex items-center gap-1"><Heart className="h-3 w-3" />{formatNumber(video.like_count)}</span>
                <span className="flex items-center gap-1"><MessageCircle className="h-3 w-3" />{formatNumber(video.comment_count)}</span>
                <span className="flex items-center gap-1"><Share2 className="h-3 w-3" />{formatNumber(video.share_count)}</span>
              </div>
              <div className="flex items-center justify-between mt-2">
                <span className={`px-2 py-0.5 text-xs rounded-full ${STATUS_COLORS[video.status] || "bg-gray-100 text-gray-800"}`}>
                  {video.status}
                </span>
                <span className="text-xs text-gray-400">
                  {video.create_time ? new Date(video.create_time).toLocaleDateString() : ""}
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {!loading && data?.items.length === 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <p className="text-gray-500">No videos found. Sync your videos from TikTok to get started.</p>
        </div>
      )}

      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-gray-500">Page {data.page} of {data.total_pages} ({data.total} total)</p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
              disabled={page >= data.total_pages}
              className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {loading && <div className="text-center py-8 text-gray-500">Loading videos...</div>}
    </div>
  );
}
