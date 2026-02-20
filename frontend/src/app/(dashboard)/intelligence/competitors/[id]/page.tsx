"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Users,
  Eye,
  Film,
  Heart,
  MessageCircle,
  Share2,
  ThumbsUp,
} from "lucide-react";

interface CompetitorProfile {
  id: string;
  username: string;
  display_name: string;
  bio: string;
  follower_count: number;
  following_count: number;
  likes_count: number;
  video_count: number;
  avg_engagement_rate: number;
}

interface CompetitorVideo {
  id: string;
  title: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  created_at: string;
}

const MOCK_PROFILE: CompetitorProfile = {
  id: "comp-1",
  username: "competitor_brand_1",
  display_name: "Brand Alpha",
  bio: "Official TikTok account for Brand Alpha. Shop our latest collection!",
  follower_count: 2_450_000,
  following_count: 312,
  likes_count: 48_900_000,
  video_count: 487,
  avg_engagement_rate: 4.8,
};

const MOCK_VIDEOS: CompetitorVideo[] = [
  { id: "v1", title: "New Collection Drop", views: 1_240_000, likes: 89_000, comments: 3_200, shares: 12_400, created_at: "2026-02-18T14:00:00Z" },
  { id: "v2", title: "Behind the Scenes", views: 890_000, likes: 67_000, comments: 2_100, shares: 8_900, created_at: "2026-02-16T10:00:00Z" },
  { id: "v3", title: "Customer Unboxing", views: 2_100_000, likes: 145_000, comments: 5_600, shares: 23_000, created_at: "2026-02-14T16:30:00Z" },
  { id: "v4", title: "Product Tutorial", views: 560_000, likes: 34_000, comments: 1_800, shares: 5_600, created_at: "2026-02-12T12:00:00Z" },
  { id: "v5", title: "Valentine's Day Special", views: 3_400_000, likes: 234_000, comments: 8_900, shares: 45_000, created_at: "2026-02-10T09:00:00Z" },
  { id: "v6", title: "Trending Challenge", views: 1_780_000, likes: 112_000, comments: 4_300, shares: 18_700, created_at: "2026-02-08T15:00:00Z" },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export default function CompetitorDetailPage() {
  const params = useParams();
  const router = useRouter();
  const competitorId = params.id as string;
  const [profile] = useState<CompetitorProfile>(MOCK_PROFILE);
  const [videos] = useState<CompetitorVideo[]>(MOCK_VIDEOS);

  return (
    <div className="max-w-4xl">
      <button
        onClick={() => router.back()}
        className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </button>

      {/* Profile Card */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-start gap-4">
          <div className="h-16 w-16 rounded-full bg-gray-100 overflow-hidden flex-shrink-0 flex items-center justify-center">
            <Users className="h-8 w-8 text-gray-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-gray-900">
              {profile.display_name}
            </h2>
            <p className="text-sm text-gray-500 mt-0.5">@{profile.username}</p>
            <p className="text-sm text-gray-600 mt-2">{profile.bio}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <Users className="h-4 w-4 text-gray-400 mx-auto mb-1" />
            <p className="text-lg font-semibold text-gray-900">{formatNumber(profile.follower_count)}</p>
            <p className="text-xs text-gray-500">Followers</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <Eye className="h-4 w-4 text-gray-400 mx-auto mb-1" />
            <p className="text-lg font-semibold text-gray-900">{formatNumber(profile.following_count)}</p>
            <p className="text-xs text-gray-500">Following</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <ThumbsUp className="h-4 w-4 text-gray-400 mx-auto mb-1" />
            <p className="text-lg font-semibold text-gray-900">{formatNumber(profile.likes_count)}</p>
            <p className="text-xs text-gray-500">Likes</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <Film className="h-4 w-4 text-gray-400 mx-auto mb-1" />
            <p className="text-lg font-semibold text-gray-900">{formatNumber(profile.video_count)}</p>
            <p className="text-xs text-gray-500">Videos</p>
          </div>
        </div>

        <div className="mt-4 p-3 bg-green-50 rounded-lg">
          <p className="text-sm text-green-800">
            Avg. Engagement Rate: <span className="font-semibold">{profile.avg_engagement_rate}%</span>
          </p>
        </div>
      </div>

      {/* Latest Content */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Latest Content</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {videos.map((video) => (
            <div key={video.id} className="px-4 py-3 hover:bg-gray-50">
              <div className="flex items-start gap-4">
                <div className="w-20 h-14 rounded bg-gray-100 flex-shrink-0 flex items-center justify-center">
                  <Film className="h-5 w-5 text-gray-300" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{video.title}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {new Date(video.created_at).toLocaleDateString()}
                  </p>
                  <div className="flex items-center gap-4 mt-2">
                    <div className="flex items-center gap-1">
                      <Eye className="h-3.5 w-3.5 text-gray-400" />
                      <span className="text-xs text-gray-500">{formatNumber(video.views)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Heart className="h-3.5 w-3.5 text-gray-400" />
                      <span className="text-xs text-gray-500">{formatNumber(video.likes)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageCircle className="h-3.5 w-3.5 text-gray-400" />
                      <span className="text-xs text-gray-500">{formatNumber(video.comments)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Share2 className="h-3.5 w-3.5 text-gray-400" />
                      <span className="text-xs text-gray-500">{formatNumber(video.shares)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
