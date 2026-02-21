"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Users, Eye, Film, ThumbsUp, Heart, MessageCircle, Share2 } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";

interface CompetitorVideo {
  id: string;
  title: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  created_at: string;
}

const MOCK_PROFILE = {
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
  const [profile] = useState(MOCK_PROFILE);
  const [videos] = useState(MOCK_VIDEOS);

  const columns: Column<CompetitorVideo>[] = [
    {
      key: "title",
      header: "Video",
      render: (row) => (
        <div>
          <p className="text-sm font-medium text-gray-900">{row.title}</p>
          <p className="text-xs text-gray-500 mt-0.5">{new Date(row.created_at).toLocaleDateString()}</p>
        </div>
      ),
    },
    {
      key: "views",
      header: "Views",
      render: (row) => (
        <div className="flex items-center gap-1"><Eye className="h-3.5 w-3.5 text-gray-400" /><span className="text-sm text-gray-600">{formatNumber(row.views)}</span></div>
      ),
    },
    {
      key: "likes",
      header: "Likes",
      render: (row) => (
        <div className="flex items-center gap-1"><Heart className="h-3.5 w-3.5 text-gray-400" /><span className="text-sm text-gray-600">{formatNumber(row.likes)}</span></div>
      ),
    },
    {
      key: "comments",
      header: "Comments",
      render: (row) => (
        <div className="flex items-center gap-1"><MessageCircle className="h-3.5 w-3.5 text-gray-400" /><span className="text-sm text-gray-600">{formatNumber(row.comments)}</span></div>
      ),
    },
    {
      key: "shares",
      header: "Shares",
      render: (row) => (
        <div className="flex items-center gap-1"><Share2 className="h-3.5 w-3.5 text-gray-400" /><span className="text-sm text-gray-600">{formatNumber(row.shares)}</span></div>
      ),
    },
  ];

  return (
    <PageShell
      header={
        <>
          <button onClick={() => router.back()} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-4">
            <ArrowLeft className="h-4 w-4" /> Back
          </button>
          <div className="bg-white rounded-xl border border-gray-100 shadow-[var(--shadow-card)] p-6 mb-6">
            <div className="flex items-start gap-4">
              <div className="h-16 w-16 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                <Users className="h-8 w-8 text-gray-400" />
              </div>
              <div className="flex-1">
                <h2 className="text-lg font-semibold text-gray-900">{profile.display_name}</h2>
                <p className="text-sm text-gray-500 mt-0.5">@{profile.username}</p>
                <p className="text-sm text-gray-600 mt-2">{profile.bio}</p>
              </div>
            </div>
          </div>
          <MetricBar>
            <MetricCard label="Followers" value={formatNumber(profile.follower_count)} icon={Users} />
            <MetricCard label="Following" value={formatNumber(profile.following_count)} icon={Eye} />
            <MetricCard label="Total Likes" value={formatNumber(profile.likes_count)} icon={ThumbsUp} />
            <MetricCard label="Videos" value={formatNumber(profile.video_count)} icon={Film} />
          </MetricBar>
        </>
      }
      aside={
        <InsightPanel>
          <InsightItem
            title="Engagement rate"
            description={`${profile.avg_engagement_rate}% average engagement rate. ${profile.avg_engagement_rate > 4 ? "Above industry average." : "Below industry average."}`}
            variant={profile.avg_engagement_rate > 4 ? "success" : "warning"}
          />
          <InsightItem title="Top content" description="Valentine's Day Special had the highest views (3.4M). Holiday content performs well for this competitor." />
        </InsightPanel>
      }
    >
      <h3 className="text-sm font-semibold text-gray-900 mb-4">Latest Content ({videos.length})</h3>
      <DataTable
        columns={columns}
        data={videos}
        keyExtractor={(row) => row.id}
        emptyTitle="No content tracked"
        emptyDescription="Content will appear here once synced"
      />
    </PageShell>
  );
}
