"use client";

import { useState } from "react";
import { MessageSquare, Reply, EyeOff, Trash2, User, TrendingUp, AlertTriangle, Shield } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { ActionMenu } from "@/components/ui/action-menu";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";

interface AdComment {
  id: string;
  ad_name: string;
  ad_id: string;
  commenter_username: string;
  commenter_display_name: string;
  text: string;
  created_at: string;
  likes: number;
  is_hidden: boolean;
  replied: boolean;
}

const MOCK_COMMENTS: AdComment[] = [
  { id: "cmt-1", ad_name: "Spring Collection Ad", ad_id: "ad-101", commenter_username: "happy_shopper", commenter_display_name: "Happy Shopper", text: "Love this! Where can I get the blue one?", created_at: "2026-02-20T10:30:00Z", likes: 12, is_hidden: false, replied: false },
  { id: "cmt-2", ad_name: "Spring Collection Ad", ad_id: "ad-101", commenter_username: "curious_buyer", commenter_display_name: "Curious Buyer", text: "How long does shipping take?", created_at: "2026-02-20T09:45:00Z", likes: 5, is_hidden: false, replied: true },
  { id: "cmt-3", ad_name: "Brand Awareness Video", ad_id: "ad-102", commenter_username: "troll_account", commenter_display_name: "Random User", text: "This is a scam don't buy", created_at: "2026-02-20T08:15:00Z", likes: 0, is_hidden: false, replied: false },
  { id: "cmt-4", ad_name: "Product Demo Reel", ad_id: "ad-103", commenter_username: "tech_fan_tt", commenter_display_name: "Tech Fan", text: "Great demo! Does it come in black?", created_at: "2026-02-19T22:30:00Z", likes: 8, is_hidden: false, replied: false },
  { id: "cmt-5", ad_name: "Product Demo Reel", ad_id: "ad-103", commenter_username: "review_queen", commenter_display_name: "Review Queen", text: "Just ordered mine! Can't wait for it to arrive.", created_at: "2026-02-19T20:00:00Z", likes: 15, is_hidden: false, replied: true },
  { id: "cmt-6", ad_name: "Flash Sale Ad", ad_id: "ad-104", commenter_username: "bargain_hunter", commenter_display_name: "Bargain Hunter", text: "Is this still available? The link doesn't work.", created_at: "2026-02-19T18:00:00Z", likes: 3, is_hidden: false, replied: false },
  { id: "cmt-7", ad_name: "Brand Awareness Video", ad_id: "ad-102", commenter_username: "spam_bot_123", commenter_display_name: "Bot Account", text: "Check my profile for free stuff!!!", created_at: "2026-02-19T16:00:00Z", likes: 0, is_hidden: true, replied: false },
];

export default function AdCommentsPage() {
  const [comments, setComments] = useState<AdComment[]>(MOCK_COMMENTS);
  const [filterAd, setFilterAd] = useState("");
  const [showHidden, setShowHidden] = useState(false);
  const [search, setSearch] = useState("");

  const adNames = [...new Set(comments.map((c) => c.ad_name))];

  const filteredComments = comments.filter((c) => {
    if (filterAd && c.ad_name !== filterAd) return false;
    if (!showHidden && c.is_hidden) return false;
    if (search && !c.text.toLowerCase().includes(search.toLowerCase()) && !c.commenter_display_name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  function handleHide(commentId: string) {
    setComments((prev) =>
      prev.map((c) => (c.id === commentId ? { ...c, is_hidden: !c.is_hidden } : c))
    );
    toast.success("Comment visibility updated");
  }

  function handleDelete(commentId: string) {
    setComments((prev) => prev.filter((c) => c.id !== commentId));
    toast.success("Comment deleted");
  }

  const unrepliedCount = comments.filter((c) => !c.replied && !c.is_hidden).length;

  return (
    <>
      <PageHeader title="Ad Comments" description="Monitor and manage comments on your ad creatives" />
      <PageShell
        header={
          <MetricBar>
            <MetricCard label="Total Comments" value={comments.length} icon={MessageSquare} iconColor="text-coral" />
            <MetricCard label="Unreplied" value={unrepliedCount} icon={Reply} iconColor="text-warning" />
            <MetricCard label="Hidden" value={comments.filter((c) => c.is_hidden).length} icon={EyeOff} iconColor="text-gray-500" />
            <MetricCard label="Replied" value={comments.filter((c) => c.replied).length} icon={Reply} iconColor="text-success" />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="Engagement"
              description="Comment engagement is up 24% this week. Most comments are product questions."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Unreplied Comments"
              description={`${unrepliedCount} comments are awaiting a reply. Respond within 2 hours for best engagement.`}
              variant="warning"
              action={{ label: "Reply to comments", onClick: () => {} }}
            />
            <InsightItem
              icon={<Shield className="h-4 w-4 text-danger" />}
              title="Spam Detected"
              description="1 comment flagged as potential spam. Review and hide if necessary."
              variant="danger"
            />
          </InsightPanel>
        }
      >
        <FilterBar
          searchValue={search}
          onSearchChange={setSearch}
          searchPlaceholder="Search comments..."
        >
          <FilterDropdown
            label="All Ads"
            value={filterAd}
            options={adNames.map((name) => ({ label: name, value: name }))}
            onChange={setFilterAd}
          />
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
            <input
              type="checkbox"
              checked={showHidden}
              onChange={(e) => setShowHidden(e.target.checked)}
              className="rounded border-gray-300"
            />
            Show hidden
          </label>
        </FilterBar>

        {/* Comments List */}
        <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
          <div className="divide-y divide-gray-100">
            {filteredComments.map((comment) => (
              <div
                key={comment.id}
                className={cn("px-4 py-4 hover:bg-gray-50 transition-colors", comment.is_hidden && "opacity-50")}
              >
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 text-sm font-medium flex-shrink-0">
                    {comment.commenter_display_name[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-gray-900">{comment.commenter_display_name}</span>
                      <span className="text-xs text-gray-400">@{comment.commenter_username}</span>
                      <span className="text-xs text-gray-400">{new Date(comment.created_at).toLocaleDateString()}</span>
                      {comment.replied && (
                        <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] rounded-full bg-success/10 text-success border border-success/20">
                          <Reply className="h-2.5 w-2.5" />
                          Replied
                        </span>
                      )}
                      {comment.is_hidden && (
                        <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] rounded-full bg-gray-100 text-gray-600">
                          <EyeOff className="h-2.5 w-2.5" />
                          Hidden
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700">{comment.text}</p>
                    <div className="flex items-center gap-4 mt-2">
                      <span className="text-xs text-gray-400">
                        on <span className="font-medium text-gray-500">{comment.ad_name}</span>
                      </span>
                      <span className="text-xs text-gray-400">{comment.likes} likes</span>
                    </div>
                  </div>
                  <ActionMenu
                    items={[
                      { label: "Reply", icon: <Reply className="h-4 w-4" />, onClick: () => toast.info("Reply coming soon") },
                      { label: comment.is_hidden ? "Unhide" : "Hide", icon: <EyeOff className="h-4 w-4" />, onClick: () => handleHide(comment.id) },
                      { label: "Delete", icon: <Trash2 className="h-4 w-4" />, onClick: () => handleDelete(comment.id), variant: "danger" },
                    ]}
                  />
                </div>
              </div>
            ))}

            {filteredComments.length === 0 && (
              <div className="px-4 py-12 text-center text-gray-500">
                <MessageSquare className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm">No comments found</p>
              </div>
            )}
          </div>
        </div>
      </PageShell>
    </>
  );
}
