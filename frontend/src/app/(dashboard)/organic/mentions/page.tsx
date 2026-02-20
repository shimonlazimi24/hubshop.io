"use client";

import { useState } from "react";
import {
  AtSign,
  Hash,
  TrendingUp,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Minus,
  User,
  Clock,
} from "lucide-react";
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
  {
    id: "mn-1",
    userName: "@beautylover99",
    text: "Just tried @yourbrand's new serum and my skin is glowing! Absolutely love it!",
    platform: "TikTok",
    sentiment: "positive",
    timestamp: "2026-02-20T09:30:00Z",
    likes: 1_240,
  },
  {
    id: "mn-2",
    userName: "@skincare_daily",
    text: "Comparing @yourbrand with @competitor - honest review coming tomorrow!",
    platform: "TikTok",
    sentiment: "neutral",
    timestamp: "2026-02-20T08:45:00Z",
    likes: 890,
  },
  {
    id: "mn-3",
    userName: "@realreviews_",
    text: "@yourbrand shipping took forever. 2 weeks and still waiting.",
    platform: "TikTok",
    sentiment: "negative",
    timestamp: "2026-02-20T07:20:00Z",
    likes: 234,
  },
  {
    id: "mn-4",
    userName: "@makeup_queen",
    text: "The @yourbrand palette is chef's kiss. Perfect for everyday looks.",
    platform: "TikTok",
    sentiment: "positive",
    timestamp: "2026-02-19T22:00:00Z",
    likes: 3_450,
  },
  {
    id: "mn-5",
    userName: "@trendwatcher",
    text: "Has anyone tried @yourbrand? Seeing it everywhere on my FYP.",
    platform: "TikTok",
    sentiment: "neutral",
    timestamp: "2026-02-19T20:15:00Z",
    likes: 567,
  },
  {
    id: "mn-6",
    userName: "@deals_finder",
    text: "@yourbrand having a secret sale right now! Use code SAVE20.",
    platform: "TikTok",
    sentiment: "positive",
    timestamp: "2026-02-19T18:30:00Z",
    likes: 2_100,
  },
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

export default function MentionsPage() {
  const [sentimentFilter, setSentimentFilter] = useState<"all" | "positive" | "neutral" | "negative">("all");

  const filteredMentions = sentimentFilter === "all"
    ? MOCK_MENTIONS
    : MOCK_MENTIONS.filter((m) => m.sentiment === sentimentFilter);

  return (
    <div className="max-w-6xl">
      {/* Top Mentions */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-gray-900">Recent Mentions</h2>
          <div className="flex gap-2">
            {(["all", "positive", "neutral", "negative"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setSentimentFilter(f)}
                className={cn(
                  "px-3 py-1.5 text-sm rounded-md transition-colors capitalize",
                  sentimentFilter === f
                    ? "bg-gray-900 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                )}
              >
                {f}
              </button>
            ))}
          </div>
        </div>
        <div className="space-y-3">
          {filteredMentions.map((mention) => (
            <div
              key={mention.id}
              className="rounded-xl border border-gray-100 bg-white p-5"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple/10">
                    <User className="h-4 w-4 text-purple" />
                  </div>
                  <div>
                    <span className="text-sm font-semibold text-gray-900">{mention.userName}</span>
                    <span className="text-xs text-gray-400 ml-2 inline-flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatTime(mention.timestamp)}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500 flex items-center gap-1">
                    <ThumbsUp className="h-3 w-3" />
                    {formatNumber(mention.likes)}
                  </span>
                  <span
                    className={cn(
                      "inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full",
                      mention.sentiment === "positive"
                        ? "bg-green-100 text-green-700"
                        : mention.sentiment === "negative"
                        ? "bg-red-100 text-red-700"
                        : "bg-gray-100 text-gray-600"
                    )}
                  >
                    {mention.sentiment === "positive" ? (
                      <ThumbsUp className="h-3 w-3" />
                    ) : mention.sentiment === "negative" ? (
                      <ThumbsDown className="h-3 w-3" />
                    ) : (
                      <Minus className="h-3 w-3" />
                    )}
                    {mention.sentiment}
                  </span>
                </div>
              </div>
              <p className="text-sm text-gray-700">{mention.text}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Frequent Keywords */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">
            Frequent Keywords
          </h2>
          <div className="rounded-xl border border-gray-100 bg-white p-5">
            <div className="space-y-3">
              {MOCK_KEYWORDS.map((kw) => (
                <div key={kw.word} className="flex items-center gap-3">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <MessageSquare className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" />
                    <span className="text-sm text-gray-900 font-medium">{kw.word}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-purple rounded-full"
                        style={{ width: `${(kw.count / MOCK_KEYWORDS[0].count) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 w-8 text-right">{kw.count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Frequent Hashtags */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">
            Frequent Hashtags
          </h2>
          <div className="rounded-xl border border-gray-100 bg-white p-5">
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
      </div>
    </div>
  );
}
