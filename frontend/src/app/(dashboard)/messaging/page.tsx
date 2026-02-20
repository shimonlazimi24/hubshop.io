"use client";

import { useState } from "react";
import Link from "next/link";
import {
  MessageSquare,
  Mail,
  Bot,
  TrendingUp,
  Clock,
  User,
  ArrowRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const KPI_CARDS = [
  {
    label: "Active Conversations",
    value: 24,
    icon: MessageSquare,
    color: "text-purple bg-purple/5 border-purple/10",
    iconColor: "text-purple",
  },
  {
    label: "Messages Today",
    value: 156,
    icon: Mail,
    color: "text-emerald-600 bg-emerald-50 border-emerald-100",
    iconColor: "text-emerald-500",
  },
  {
    label: "Auto-Messages",
    value: 89,
    icon: Bot,
    color: "text-blue-600 bg-blue-50 border-blue-100",
    iconColor: "text-blue-500",
  },
  {
    label: "Response Rate",
    value: "94%",
    icon: TrendingUp,
    color: "text-coral bg-coral/5 border-coral/10",
    iconColor: "text-coral",
  },
];

interface Conversation {
  id: string;
  userName: string;
  lastMessage: string;
  timestamp: string;
  unread: number;
  status: "active" | "resolved" | "waiting";
}

const MOCK_CONVERSATIONS: Conversation[] = [
  {
    id: "conv-1",
    userName: "Sarah Johnson",
    lastMessage: "When will my order ship? I placed it 3 days ago.",
    timestamp: "2026-02-20T10:15:00Z",
    unread: 2,
    status: "active",
  },
  {
    id: "conv-2",
    userName: "Mike Chen",
    lastMessage: "Thanks for the quick response! The product is amazing.",
    timestamp: "2026-02-20T09:45:00Z",
    unread: 0,
    status: "resolved",
  },
  {
    id: "conv-3",
    userName: "Emma Wilson",
    lastMessage: "Do you have this in size M? The listing shows out of stock.",
    timestamp: "2026-02-20T09:30:00Z",
    unread: 1,
    status: "active",
  },
  {
    id: "conv-4",
    userName: "Alex Rivera",
    lastMessage: "I'd like to return this item. How do I start the process?",
    timestamp: "2026-02-20T08:20:00Z",
    unread: 3,
    status: "waiting",
  },
  {
    id: "conv-5",
    userName: "Lisa Park",
    lastMessage: "Can you send me more product photos before I buy?",
    timestamp: "2026-02-20T07:55:00Z",
    unread: 1,
    status: "active",
  },
  {
    id: "conv-6",
    userName: "James Taylor",
    lastMessage: "The discount code doesn't seem to work. Can you help?",
    timestamp: "2026-02-19T22:30:00Z",
    unread: 0,
    status: "resolved",
  },
  {
    id: "conv-7",
    userName: "Nina Patel",
    lastMessage: "Is this product available for international shipping?",
    timestamp: "2026-02-19T21:15:00Z",
    unread: 2,
    status: "waiting",
  },
  {
    id: "conv-8",
    userName: "David Kim",
    lastMessage: "Love your store! Do you have a loyalty program?",
    timestamp: "2026-02-19T20:00:00Z",
    unread: 0,
    status: "resolved",
  },
];

function formatTime(ts: string): string {
  const date = new Date(ts);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 1) return "Just now";
  if (hours < 24) return `${hours}h ago`;
  return date.toLocaleDateString();
}

export default function MessagingOverviewPage() {
  const [loading] = useState(false);

  return (
    <div className="max-w-6xl">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {KPI_CARDS.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.label}
              className="rounded-xl border border-gray-100 bg-white p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <div
                  className={cn(
                    "flex h-9 w-9 items-center justify-center rounded-lg",
                    card.color
                  )}
                >
                  <Icon className={cn("h-[18px] w-[18px]", card.iconColor)} />
                </div>
              </div>
              {loading ? (
                <div className="h-8 w-16 mb-2 rounded bg-gray-100 animate-pulse" />
              ) : (
                <p className="text-2xl font-semibold text-gray-900">
                  {typeof card.value === "number"
                    ? card.value.toLocaleString()
                    : card.value}
                </p>
              )}
              <p className="text-xs text-gray-400 mt-1">{card.label}</p>
            </div>
          );
        })}
      </div>

      {/* Conversations */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Recent Conversations
        </h2>
        <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
          {MOCK_CONVERSATIONS.map((conv) => (
            <Link
              key={conv.id}
              href={`/messaging/${conv.id}`}
              className="flex items-center gap-4 px-5 py-4 hover:bg-gray-50 transition-colors group"
            >
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-full flex-shrink-0",
                  conv.status === "active"
                    ? "bg-purple/10"
                    : conv.status === "waiting"
                    ? "bg-yellow-50"
                    : "bg-gray-100"
                )}
              >
                <User
                  className={cn(
                    "h-5 w-5",
                    conv.status === "active"
                      ? "text-purple"
                      : conv.status === "waiting"
                      ? "text-yellow-500"
                      : "text-gray-400"
                  )}
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-0.5">
                  <h3 className="text-sm font-semibold text-gray-900">
                    {conv.userName}
                  </h3>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400 flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatTime(conv.timestamp)}
                    </span>
                    {conv.unread > 0 && (
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-coral text-[10px] font-semibold text-white">
                        {conv.unread}
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-xs text-gray-500 truncate">{conv.lastMessage}</p>
              </div>
              <ArrowRight className="h-4 w-4 text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
