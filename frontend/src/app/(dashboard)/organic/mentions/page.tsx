"use client";

import { useState } from "react";
import { AtSign, Hash, TrendingUp, ThumbsUp, ThumbsDown, Minus, User, Clock, MessageSquare } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { cn } from "@/lib/utils";

interface Mention {
  id: string;
  userName: string;
  text: string;
  platform: string;
  sentiment: "positive" | "neutral" | "negative";
  timestamp: string;
  likes: number;
}

const MOCK_MENTIONS: Mention[] = [
  { id: "mn-1", userName: "@beautylover99", text: "Just tried @yourbrand's new serum and my skin is glowing! Absolutely love it!", platform: "TikTok", sentiment: "positive", timestamp: "2026-02-20T09:30:00Z", likes: 1_240 },
  { id: "mn-2", userName: "@skincare_daily", text: "Comparing @yourbrand with @competitor - honest review coming tomorrow!", platform: "TikTok", sentiment: "neutral", timestamp: "2026-02-20T08:45:00Z", likes: 890 },
  { id: "mn-3", userName: "@realreviews_", text: "@yourbrand shipping took forever. 2 weeks and still waiting.", platform: "TikTok", sentiment: "negative", timestamp: "2026-02-20T07:20:00Z", likes: 234 },
  { id: "mn-4", userName: "@makeup_queen", text: "The @yourbrand palette is chef's kiss. Perfect for everyday looks.", platform: "TikTok", sentiment: "positive", timestamp: "2026-02-19T22:00:00Z", likes: 3_450 },
  { id: "mn-5", userName: "@trendwatcher", text: "Has anyone tried @yourbrand? Seeing it everywhere on my FYP.", platform: "TikTok", sentiment: "neutral", timestamp: "2026-02-19T20:15:00Z", likes: 567 },
  { id: "mn-6", userName: "@deals_finder", text: "@yourbrand having a secret sale right now! Use code SAVE20.", platform: "TikTok", sentiment: "positive", timestamp: "2026-02-19T18:30:00Z", likes: 2_100 },
];

const MOCK_KEYWORDS = [
  { word: "skincare", count: 89 },
  { word: "serum", count: 67 },
  { word: "glow", count: 54 },
  { word: "routine", count: 48 },
  { word: "review", count: 42 },
  { word: "affordable", count: 38 },
  { word: "shipping", count: 31 },
  { word: "natural", count: 28 },
];

const MOCK_HASHTAGS = [
  { tag: "#yourbrand", posts: 12_400, growth: 18.5 },
  { tag: "#yourbrandreview", posts: 4_560, growth: 24.3 },
  { tag: "#skincareroutine", posts: 89_000, growth: 5.2 },
  { tag: "#tiktokmademebuyit", posts: 52_000_000, growth: 12.1 },
  { tag: "#beautytok", posts: 28_000_000, growth: 8.9 },
  { tag: "#yourbrandglow", posts: 1_200, growth: 45.7 },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function formatTime(ts: string): string {
  const date = new Date(ts);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 1) return "Just now";
  if (hours < 24) return `${hours}h ago`;
  return date.toLocaleDateString();
}

const SENTIMENT_MAP: Record<string, StatusVariant> = {
  positive: "active",
  neutral: "draft",
  negative: "error",
};

export default function MentionsPage() {
  const [sentimentFilter, setSentimentFilter] = useState("");
  const [search, setSearch] = useState("");

  const filtered = MOCK_MENTIONS.filter((m) => {
    if (sentimentFilter && m.sentiment !== sentimentFilter) return false;
    if (search && !m.text.toLowerCase().includes(search.toLowerCase()) && !m.userName.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const positiveCount = MOCK_MENTIONS.filter((m) => m.sentiment === "positive").length;
  const negativeCount = MOCK_MENTIONS.filter((m) => m.sentiment === "negative").length;

  const columns: Column<Mention>[] = [
    {
      key: "mention",
      header: "Mention",
      render: (row) => (
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-semibold text-gray-900">{row.userName}</span>
            <span className="text-xs text-gray-400 flex items-center gap-1"><Clock className="h-3 w-3" />{formatTime(row.timestamp)}</span>
          </div>
          <p className="text-sm text-gray-700">{row.text}</p>
        </div>
      ),
    },
    {
      key: "sentiment",
      header: "Sentiment",
      render: (row) => <StatusBadge variant={SENTIMENT_MAP[row.sentiment] || "draft"} label={row.sentiment} />,
    },
    {
      key: "likes",
      header: "Likes",
      render: (row) => (
        <span className="text-sm text-gray-500 flex items-center gap-1"><ThumbsUp className="h-3 w-3" />{formatNumber(row.likes)}</span>
      ),
    },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Total Mentions" value={MOCK_MENTIONS.length} icon={AtSign} />
          <MetricCard label="Positive" value={positiveCount} icon={ThumbsUp} trend={{ value: positiveCount, direction: "up" }} />
          <MetricCard label="Negative" value={negativeCount} icon={ThumbsDown} trend={{ value: negativeCount, direction: negativeCount > 2 ? "down" : "flat" }} />
          <MetricCard label="Branded Hashtags" value={MOCK_HASHTAGS.length} icon={Hash} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Sentiment overview" description={`${Math.round((positiveCount / MOCK_MENTIONS.length) * 100)}% positive sentiment. Monitor negative mentions for shipping complaints.`} variant={positiveCount > negativeCount ? "success" : "warning"} />
          <InsightItem title="Top hashtag growth" description="#yourbrandglow is up 45.7% - consider amplifying this user-generated tag." variant="success" />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search mentions..."
      >
        <FilterDropdown
          label="Sentiment"
          value={sentimentFilter}
          onChange={setSentimentFilter}
          options={[
            { label: "Positive", value: "positive" },
            { label: "Neutral", value: "neutral" },
            { label: "Negative", value: "negative" },
          ]}
        />
      </FilterBar>

      <DataTable
        columns={columns}
        data={filtered}
        keyExtractor={(row) => row.id}
        emptyTitle="No mentions found"
        emptyDescription="Brand mentions will appear here as they are detected"
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        {/* Keywords */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-[var(--shadow-card)] p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Frequent Keywords</h3>
          <div className="space-y-3">
            {MOCK_KEYWORDS.map((kw) => (
              <div key={kw.word} className="flex items-center gap-3">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <MessageSquare className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" />
                  <span className="text-sm text-gray-900 font-medium">{kw.word}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-purple rounded-full" style={{ width: `${(kw.count / MOCK_KEYWORDS[0].count) * 100}%` }} />
                  </div>
                  <span className="text-xs text-gray-500 w-8 text-right">{kw.count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Hashtags */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-[var(--shadow-card)] p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Frequent Hashtags</h3>
          <div className="space-y-3">
            {MOCK_HASHTAGS.map((ht) => (
              <div key={ht.tag} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Hash className="h-3.5 w-3.5 text-purple" />
                  <span className="text-sm font-medium text-gray-900">{ht.tag}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-500">{formatNumber(ht.posts)} posts</span>
                  <div className="flex items-center gap-1">
                    <TrendingUp className="h-3 w-3 text-green-500" />
                    <span className="text-xs font-medium text-green-600">+{ht.growth}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageShell>
  );
}
