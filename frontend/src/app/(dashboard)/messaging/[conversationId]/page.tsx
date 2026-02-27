"use client";

import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Send, User, Bot, Clock, MoreHorizontal, RefreshCw } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { EmptyState } from "@/components/ui/empty-state";
import { toast } from "@/lib/toast-store";
import { getMessagingMessages, sendMessagingMessage } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  sender: "user" | "merchant" | "auto";
  text: string;
  timestamp: string;
}

function mapMessage(raw: Record<string, unknown>): Message {
  const direction = String(raw.direction || "INBOUND");
  return {
    id: String(raw.id || raw.tiktok_message_id || Math.random()),
    sender: direction === "OUTBOUND" ? "merchant" : "user",
    text: String(raw.content || ""),
    timestamp: String(raw.sent_at || raw.created_at || new Date().toISOString()),
  };
}

function formatTimestamp(ts: string): string {
  const date = new Date(ts);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function ConversationDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const conversationId = params.conversationId as string;
  const connectedAccountId = searchParams.get("account");

  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [newMessage, setNewMessage] = useState("");

  const token = getAccessToken();

  useEffect(() => {
    loadMessages();
  }, [conversationId, connectedAccountId]);

  function loadMessages() {
    if (!token || !connectedAccountId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    getMessagingMessages(conversationId, connectedAccountId, token)
      .then((data) => {
        setMessages((data.messages || []).map(mapMessage));
      })
      .catch((err) => {
        console.error(err);
        toast.error("Failed to load messages");
      })
      .finally(() => setLoading(false));
  }

  async function handleSend() {
    if (!newMessage.trim() || !token || !connectedAccountId) return;
    const content = newMessage.trim();
    setNewMessage("");
    setSending(true);

    // Optimistic update
    const optimistic: Message = {
      id: `temp-${Date.now()}`,
      sender: "merchant",
      text: content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimistic]);

    try {
      await sendMessagingMessage(conversationId, connectedAccountId, content, token);
    } catch {
      toast.error("Failed to send message");
      setMessages((prev) => prev.filter((m) => m.id !== optimistic.id));
      setNewMessage(content);
    } finally {
      setSending(false);
    }
  }

  if (!connectedAccountId) {
    return (
      <PageShell>
        <EmptyState
          icon={ArrowLeft}
          title="Missing account"
          description="Go back to conversations to select a conversation."
        />
      </PageShell>
    );
  }

  return (
    <PageShell
      aside={
        <InsightPanel>
          <InsightItem title="Conversation" description={`Conversation ${conversationId} — ${messages.length} messages loaded`} />
          <InsightItem title="Tip" description="Messages are fetched from TikTok Business Messaging API. Refresh to see new messages." variant="default" />
        </InsightPanel>
      }
    >
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link href="/messaging" className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors">
          <ArrowLeft className="h-4 w-4 text-gray-600" />
        </Link>
        <div className="flex items-center gap-3 flex-1">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple/10">
            <User className="h-5 w-5 text-purple" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-gray-900">Conversation</h2>
            <p className="text-xs text-gray-500">{messages.length} messages</p>
          </div>
        </div>
        <button onClick={loadMessages} disabled={loading} className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors">
          <RefreshCw className={cn("h-4 w-4 text-gray-600", loading && "animate-spin")} />
        </button>
      </div>

      {/* Messages */}
      <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] overflow-hidden">
        <div className="p-5 space-y-4 min-h-[400px] max-h-[500px] overflow-y-auto">
          {loading && messages.length === 0 ? (
            <div className="flex items-center justify-center h-[400px] text-sm text-gray-400">Loading messages...</div>
          ) : messages.length === 0 ? (
            <div className="flex items-center justify-center h-[400px] text-sm text-gray-400">No messages yet</div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={cn("flex gap-3", msg.sender === "merchant" || msg.sender === "auto" ? "justify-start" : "justify-end")}>
                {(msg.sender === "merchant" || msg.sender === "auto") && (
                  <div className={cn("flex h-8 w-8 items-center justify-center rounded-full flex-shrink-0", msg.sender === "auto" ? "bg-blue-50" : "bg-emerald-50")}>
                    {msg.sender === "auto" ? <Bot className="h-4 w-4 text-blue-500" /> : <User className="h-4 w-4 text-emerald-500" />}
                  </div>
                )}
                <div className={cn("max-w-[70%] rounded-xl px-4 py-2.5", msg.sender === "user" ? "bg-coral text-white" : msg.sender === "auto" ? "bg-blue-50 text-gray-900" : "bg-gray-100 text-gray-900")}>
                  {msg.sender === "auto" && <p className="text-[10px] font-medium text-blue-500 mb-1">Auto-reply</p>}
                  <p className="text-sm leading-relaxed">{msg.text}</p>
                  <p className={cn("text-[10px] mt-1 flex items-center gap-1", msg.sender === "user" ? "text-white/70" : "text-gray-400")}>
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
            ))
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-100 p-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder="Type a message..."
              className="flex-1 px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
            />
            <button
              onClick={handleSend}
              disabled={!newMessage.trim() || sending}
              className="flex items-center gap-1.5 rounded-lg bg-coral px-4 py-2.5 text-sm font-medium text-white hover:bg-coral/90 disabled:opacity-50 transition-colors"
            >
              <Send className="h-4 w-4" />
              {sending ? "Sending..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </PageShell>
  );
}
