"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Heart, Users, Eye, ThumbsUp, Film, TrendingUp } from "lucide-react";
import { getCreator, saveCreator, type CreatorDetail } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { StatusBadge } from "@/components/ui/status-badge";

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

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
      .catch(() => toast.error("Failed to load creator"))
      .finally(() => setLoading(false));
  }, [creatorId]);

  async function handleSave() {
    if (!token || !creator) return;
    try {
      await saveCreator(creator.id, !creator.is_saved, token);
      setCreator({ ...creator, is_saved: !creator.is_saved });
      toast.success(creator.is_saved ? "Creator removed from saved" : "Creator saved");
    } catch {
      toast.error("Failed to update saved status");
    }
  }

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Loading creator details...</div>;
  }

  if (!creator) {
    return <div className="text-center py-8 text-gray-500">Creator not found.</div>;
  }

  const engagementRate = creator.engagement_rate ? parseFloat(creator.engagement_rate) : 0;

  return (
    <PageShell
      header={
        <>
          <button onClick={() => router.back()} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-4">
            <ArrowLeft className="h-4 w-4" /> Back
          </button>
          <div className="bg-white rounded-xl border border-gray-100 shadow-[var(--shadow-card)] p-6 mb-6">
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
                  {creator.tier && <StatusBadge variant="syncing" label={creator.tier} />}
                  <button onClick={handleSave} className="ml-auto">
                    <Heart className={`h-5 w-5 transition-colors ${creator.is_saved ? "text-red-500 fill-red-500" : "text-gray-300 hover:text-red-400"}`} />
                  </button>
                </div>
                {creator.username && <p className="text-sm text-gray-500 mt-0.5">@{creator.username}</p>}
                {creator.bio && <p className="text-sm text-gray-600 mt-2">{creator.bio}</p>}
              </div>
            </div>
          </div>
          <MetricBar>
            <MetricCard label="Followers" value={formatNumber(creator.follower_count)} icon={Users} />
            <MetricCard label="Following" value={formatNumber(creator.following_count)} icon={Eye} />
            <MetricCard label="Likes" value={formatNumber(creator.likes_count)} icon={ThumbsUp} />
            <MetricCard label="Videos" value={formatNumber(creator.video_count)} icon={Film} />
            {engagementRate > 0 && (
              <MetricCard
                label="Engagement Rate"
                value={`${engagementRate.toFixed(2)}%`}
                icon={TrendingUp}
                trend={{ value: engagementRate, direction: engagementRate > 3 ? "up" : "flat" }}
              />
            )}
          </MetricBar>
        </>
      }
      aside={
        <InsightPanel>
          <InsightItem
            title="Engagement analysis"
            description={engagementRate > 5 ? "Above-average engagement rate. Great for brand partnerships." : engagementRate > 2 ? "Average engagement. Consider niche alignment." : "Below average engagement. May need content strategy review."}
            variant={engagementRate > 5 ? "success" : engagementRate > 2 ? "default" : "warning"}
          />
          <InsightItem title="Content frequency" description={`${creator.video_count} videos published. Check posting consistency for campaign fit.`} />
        </InsightPanel>
      }
    >
      {creator.audience_demographics && Object.keys(creator.audience_demographics).length > 0 && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-[var(--shadow-card)] p-6 mb-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Audience Demographics</h3>
          <pre className="text-xs text-gray-600 bg-gray-50 rounded-lg p-3 overflow-auto">
            {JSON.stringify(creator.audience_demographics, null, 2)}
          </pre>
        </div>
      )}

      {creator.categories && Object.keys(creator.categories).length > 0 && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-[var(--shadow-card)] p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Categories</h3>
          <pre className="text-xs text-gray-600 bg-gray-50 rounded-lg p-3 overflow-auto">
            {JSON.stringify(creator.categories, null, 2)}
          </pre>
        </div>
      )}
    </PageShell>
  );
}
