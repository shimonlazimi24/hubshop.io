"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Eye,
  Gift,
  MessageCircle,
  Heart,
  UserPlus,
  Radio,
  BarChart3,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface LiveEvent {
  id: string;
  type: "comment" | "gift" | "like" | "follow" | "join" | "share";
  username: string;
  content: string;
  timestamp: string;
}

const EVENT_CONFIG = {
  comment: { icon: MessageCircle, color: "bg-blue-100 text-blue-800", iconColor: "text-blue-500" },
  gift: { icon: Gift, color: "bg-yellow-100 text-yellow-800", iconColor: "text-yellow-500" },
  like: { icon: Heart, color: "bg-pink-100 text-pink-800", iconColor: "text-pink-500" },
  follow: { icon: UserPlus, color: "bg-green-100 text-green-800", iconColor: "text-green-500" },
  join: { icon: Eye, color: "bg-purple-100 text-purple-800", iconColor: "text-purple-500" },
  share: { icon: Radio, color: "bg-orange-100 text-orange-800", iconColor: "text-orange-500" },
};

const MOCK_EVENTS: LiveEvent[] = [
  { id: "e1", type: "comment", username: "user_fan_1", content: "Love this product!", timestamp: "2026-02-20T10:45:12Z" },
  { id: "e2", type: "gift", username: "big_supporter", content: "Sent Rose x5", timestamp: "2026-02-20T10:45:08Z" },
  { id: "e3", type: "like", username: "viewer_42", content: "Liked the stream", timestamp: "2026-02-20T10:45:05Z" },
  { id: "e4", type: "follow", username: "new_follower", content: "Started following", timestamp: "2026-02-20T10:44:58Z" },
  { id: "e5", type: "comment", username: "shopper_tt", content: "How much is this?", timestamp: "2026-02-20T10:44:52Z" },
  { id: "e6", type: "gift", username: "vip_viewer", content: "Sent Galaxy x1", timestamp: "2026-02-20T10:44:45Z" },
  { id: "e7", type: "join", username: "curious_viewer", content: "Joined the stream", timestamp: "2026-02-20T10:44:40Z" },
  { id: "e8", type: "comment", username: "beauty_fan", content: "Can you show the shade options?", timestamp: "2026-02-20T10:44:35Z" },
  { id: "e9", type: "like", username: "happy_watcher", content: "Liked the stream", timestamp: "2026-02-20T10:44:30Z" },
  { id: "e10", type: "share", username: "sharer_99", content: "Shared to friends", timestamp: "2026-02-20T10:44:25Z" },
  { id: "e11", type: "comment", username: "deal_hunter", content: "Will there be a discount?", timestamp: "2026-02-20T10:44:20Z" },
  { id: "e12", type: "gift", username: "generous_one", content: "Sent Lion x2", timestamp: "2026-02-20T10:44:15Z" },
  { id: "e13", type: "follow", username: "newbie_tiktok", content: "Started following", timestamp: "2026-02-20T10:44:10Z" },
  { id: "e14", type: "comment", username: "first_timer", content: "First time here, love the vibe!", timestamp: "2026-02-20T10:44:05Z" },
  { id: "e15", type: "like", username: "silent_viewer", content: "Liked the stream", timestamp: "2026-02-20T10:44:00Z" },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export default function LiveSessionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;
  const [events] = useState<LiveEvent[]>(MOCK_EVENTS);

  const stats = {
    viewers: 12_400,
    gifts: 342,
    comments: events.filter((e) => e.type === "comment").length,
    likes: events.filter((e) => e.type === "like").length,
  };

  return (
    <div className="max-w-4xl">
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>
        <Link
          href={`/live/${sessionId}/analytics`}
          className="flex items-center gap-1.5 rounded-lg bg-gray-900 px-3 py-2 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
        >
          <BarChart3 className="h-4 w-4" />
          View Analytics
        </Link>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-3 mb-6">
        <div className="rounded-xl border border-gray-100 bg-white p-4 text-center">
          <Eye className="h-4 w-4 text-purple mx-auto mb-1" />
          <p className="text-lg font-semibold text-gray-900">{formatNumber(stats.viewers)}</p>
          <p className="text-xs text-gray-400">Viewers</p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white p-4 text-center">
          <Gift className="h-4 w-4 text-yellow-500 mx-auto mb-1" />
          <p className="text-lg font-semibold text-gray-900">{formatNumber(stats.gifts)}</p>
          <p className="text-xs text-gray-400">Gifts</p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white p-4 text-center">
          <MessageCircle className="h-4 w-4 text-blue-500 mx-auto mb-1" />
          <p className="text-lg font-semibold text-gray-900">{stats.comments}</p>
          <p className="text-xs text-gray-400">Comments</p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white p-4 text-center">
          <Heart className="h-4 w-4 text-pink-500 mx-auto mb-1" />
          <p className="text-lg font-semibold text-gray-900">{stats.likes}</p>
          <p className="text-xs text-gray-400">Likes</p>
        </div>
      </div>

      {/* Session Info */}
      <div className="flex items-center gap-2 mb-4">
        <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
        <span className="text-sm font-medium text-gray-900">Live Event Feed</span>
        <span className="text-xs text-gray-400">Session: {sessionId}</span>
      </div>

      {/* Event Feed */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="divide-y divide-gray-100">
          {events.map((event) => {
            const config = EVENT_CONFIG[event.type];
            const Icon = config.icon;
            return (
              <div key={event.id} className="px-4 py-3 flex items-start gap-3 hover:bg-gray-50">
                <span className={cn("inline-flex h-7 w-7 items-center justify-center rounded-full flex-shrink-0", config.color)}>
                  <Icon className={cn("h-3.5 w-3.5", config.iconColor)} />
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-baseline gap-2">
                    <span className="text-sm font-medium text-gray-900">@{event.username}</span>
                    <span className={cn("px-1.5 py-0.5 text-[10px] font-medium rounded", config.color)}>
                      {event.type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-0.5">{event.content}</p>
                </div>
                <span className="text-xs text-gray-400 flex-shrink-0">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
