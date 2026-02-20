"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Heart,
  Users,
  Eye,
  ThumbsUp,
  Film,
} from "lucide-react";
import { getCreator, saveCreator, type CreatorDetail } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function CreatorDetailPage() {
  const params = useParams();
  const router = useRouter();
  const creatorId = params.id as string;
  const [creator, setCreator] = useState<CreatorDetail | null>(null);
  const [loading, setLoading] = useState(true);

  const token = getAccessToken();

  useEffect(() => {
    if (!token || !creatorId) return;
    getCreator(creatorId, token)
      .then(setCreator)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [creatorId]);

  async function handleSave() {
    if (!token || !creator) return;
    try {
      await saveCreator(creator.id, !creator.is_saved, token);
      setCreator({ ...creator, is_saved: !creator.is_saved });
    } catch (err) {
      console.error(err);
    }
  }

  function formatNumber(n: number): string {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
    return String(n);
  }

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Loading creator details...</div>;
  }

  if (!creator) {
    return <div className="text-center py-8 text-gray-500">Creator not found.</div>;
  }

  return (
    <div className="max-w-4xl">
      <button
        onClick={() => router.back()}
        className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </button>

      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-start gap-4">
          <div className="h-16 w-16 rounded-full bg-gray-100 overflow-hidden flex-shrink-0">
            {creator.avatar_url ? (
              <img src={creator.avatar_url} alt="" className="h-full w-full object-cover" />
            ) : (
              <div className="flex items-center justify-center h-full">
                <Users className="h-8 w-8 text-gray-400" />
              </div>
            )}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-semibold text-gray-900">
                {creator.display_name || creator.username || "Unknown"}
              </h2>
              {creator.tier && (
                <span className="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800">
                  {creator.tier}
                </span>
              )}
              <button onClick={handleSave} className="ml-auto">
                <Heart
                  className={`h-5 w-5 transition-colors ${
                    creator.is_saved
                      ? "text-red-500 fill-red-500"
                      : "text-gray-300 hover:text-red-400"
                  }`}
                />
              </button>
            </div>
            {creator.username && (
              <p className="text-sm text-gray-500 mt-0.5">@{creator.username}</p>
            )}
            {creator.bio && (
              <p className="text-sm text-gray-600 mt-2">{creator.bio}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <Users className="h-4 w-4 text-gray-400 mx-auto mb-1" />
            <p className="text-lg font-semibold text-gray-900">{formatNumber(creator.follower_count)}</p>
            <p className="text-xs text-gray-500">Followers</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <Eye className="h-4 w-4 text-gray-400 mx-auto mb-1" />
            <p className="text-lg font-semibold text-gray-900">{formatNumber(creator.following_count)}</p>
            <p className="text-xs text-gray-500">Following</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <ThumbsUp className="h-4 w-4 text-gray-400 mx-auto mb-1" />
            <p className="text-lg font-semibold text-gray-900">{formatNumber(creator.likes_count)}</p>
            <p className="text-xs text-gray-500">Likes</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <Film className="h-4 w-4 text-gray-400 mx-auto mb-1" />
            <p className="text-lg font-semibold text-gray-900">{formatNumber(creator.video_count)}</p>
            <p className="text-xs text-gray-500">Videos</p>
          </div>
        </div>

        {creator.engagement_rate && (
          <div className="mt-4 p-3 bg-green-50 rounded-lg">
            <p className="text-sm text-green-800">
              Engagement Rate: <span className="font-semibold">{parseFloat(creator.engagement_rate).toFixed(2)}%</span>
            </p>
          </div>
        )}
      </div>

      {creator.audience_demographics && Object.keys(creator.audience_demographics).length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <h3 className="text-sm font-medium text-gray-900 mb-4">Audience Demographics</h3>
          <pre className="text-xs text-gray-600 bg-gray-50 rounded p-3 overflow-auto">
            {JSON.stringify(creator.audience_demographics, null, 2)}
          </pre>
        </div>
      )}

      {creator.categories && Object.keys(creator.categories).length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-sm font-medium text-gray-900 mb-4">Categories</h3>
          <pre className="text-xs text-gray-600 bg-gray-50 rounded p-3 overflow-auto">
            {JSON.stringify(creator.categories, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
