"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Send,
  User,
  Bot,
  Clock,
  MoreHorizontal,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  sender: "user" | "merchant" | "auto";
  text: string;
  timestamp: string;
}

const MOCK_USER = {
  name: "Sarah Johnson",
  status: "active" as const,
  joinedAt: "2025-08-15",
  totalOrders: 5,
};

const MOCK_MESSAGES: Message[] = [
  {
    id: "m-1",
    sender: "auto",
    text: "Hi! Thanks for reaching out. Our team typically responds within 15 minutes during business hours.",
    timestamp: "2026-02-20T10:00:00Z",
  },
  {
    id: "m-2",
    sender: "user",
    text: "Hi there! I placed an order 3 days ago (Order #TTS-28491) and haven't received any shipping updates yet.",
    timestamp: "2026-02-20T10:02:00Z",
  },
  {
    id: "m-3",
    sender: "merchant",
    text: "Hello Sarah! Let me look into that for you right away.",
    timestamp: "2026-02-20T10:05:00Z",
  },
  {
    id: "m-4",
    sender: "merchant",
    text: "I found your order. It looks like it was shipped yesterday and the tracking info should update within 24 hours. Your tracking number is TK-992847381.",
    timestamp: "2026-02-20T10:07:00Z",
  },
  {
    id: "m-5",
    sender: "user",
    text: "Oh great, thank you! Do you know the estimated delivery date?",
    timestamp: "2026-02-20T10:10:00Z",
  },
  {
    id: "m-6",
    sender: "merchant",
    text: "Based on your location, you should receive it within 3-5 business days. So approximately by February 25th.",
    timestamp: "2026-02-20T10:12:00Z",
  },
  {
    id: "m-7",
    sender: "user",
    text: "Perfect, that works! One more question - can I add another item to this order?",
    timestamp: "2026-02-20T10:15:00Z",
  },
];

function formatTimestamp(ts: string): string {
  const date = new Date(ts);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function ConversationDetailPage() {
  const [newMessage, setNewMessage] = useState("");

  function handleSend() {
    if (!newMessage.trim()) return;
    // Placeholder: would send via API
    setNewMessage("");
  }

  return (
    <div className="max-w-4xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link
          href="/messaging"
          className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
        >
          <ArrowLeft className="h-4 w-4 text-gray-600" />
        </Link>
        <div className="flex items-center gap-3 flex-1">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple/10">
            <User className="h-5 w-5 text-purple" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-gray-900">{MOCK_USER.name}</h2>
            <p className="text-xs text-gray-500">
              {MOCK_USER.totalOrders} orders | Customer since {new Date(MOCK_USER.joinedAt).toLocaleDateString()}
            </p>
          </div>
        </div>
        <button className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors">
          <MoreHorizontal className="h-4 w-4 text-gray-600" />
        </button>
      </div>

      {/* Messages */}
      <div className="rounded-xl border border-gray-100 bg-white overflow-hidden">
        <div className="p-5 space-y-4 min-h-[400px] max-h-[500px] overflow-y-auto">
          {MOCK_MESSAGES.map((msg) => (
            <div
              key={msg.id}
              className={cn(
                "flex gap-3",
                msg.sender === "merchant" || msg.sender === "auto"
                  ? "justify-start"
                  : "justify-end"
              )}
            >
              {(msg.sender === "merchant" || msg.sender === "auto") && (
                <div
                  className={cn(
                    "flex h-8 w-8 items-center justify-center rounded-full flex-shrink-0",
                    msg.sender === "auto" ? "bg-blue-50" : "bg-emerald-50"
                  )}
                >
                  {msg.sender === "auto" ? (
                    <Bot className="h-4 w-4 text-blue-500" />
                  ) : (
                    <User className="h-4 w-4 text-emerald-500" />
                  )}
                </div>
              )}
              <div
                className={cn(
                  "max-w-[70%] rounded-xl px-4 py-2.5",
                  msg.sender === "user"
                    ? "bg-coral text-white"
                    : msg.sender === "auto"
                    ? "bg-blue-50 text-gray-900"
                    : "bg-gray-100 text-gray-900"
                )}
              >
                {msg.sender === "auto" && (
                  <p className="text-[10px] font-medium text-blue-500 mb-1">Auto-reply</p>
                )}
                <p className="text-sm leading-relaxed">{msg.text}</p>
                <p
                  className={cn(
                    "text-[10px] mt-1 flex items-center gap-1",
                    msg.sender === "user" ? "text-white/70" : "text-gray-400"
                  )}
                >
                  <Clock className="h-2.5 w-2.5" />
                  {formatTimestamp(msg.timestamp)}
                </p>
              </div>
              {msg.sender === "user" && (
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple/10 flex-shrink-0">
                  <User className="h-4 w-4 text-purple" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="border-t border-gray-100 p-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Type a message..."
              className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/50 focus:border-coral"
            />
            <button
              onClick={handleSend}
              disabled={!newMessage.trim()}
              className="flex items-center gap-1.5 rounded-lg bg-coral px-4 py-2.5 text-sm font-medium text-white hover:bg-coral/90 disabled:opacity-50 transition-colors"
            >
              <Send className="h-4 w-4" />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
