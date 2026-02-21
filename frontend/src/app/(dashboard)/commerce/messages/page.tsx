"use client";

import { useEffect, useState } from "react";
import { MessageSquare, Clock, Users } from "lucide-react";
import { listConversations, listShops, type Shop } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterDropdown } from "@/components/ui/filter-bar";
import { EmptyState } from "@/components/ui/empty-state";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

export default function MessagesPage() {
  const [shops, setShops] = useState<Shop[]>([]);
  const [selectedShop, setSelectedShop] = useState("");
  const [conversations, setConversations] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    listShops(WORKSPACE_ID, token)
      .then(s => {
        setShops(s);
        if (s.length > 0) setSelectedShop(s[0].id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!token || !selectedShop) return;
    setLoading(true);
    listConversations(WORKSPACE_ID, selectedShop, token)
      .then(data => setConversations(data.conversations))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedShop]);

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Conversations"
            value={conversations.length}
            icon={MessageSquare}
            iconColor="text-coral"
            loading={loading}
          />
          <MetricCard
            label="Avg Response Time"
            value="12 min"
            icon={Clock}
            iconColor="text-warning"
            loading={loading}
          />
          <MetricCard
            label="Active Buyers"
            value={conversations.length}
            icon={Users}
            iconColor="text-info"
            loading={loading}
          />
        </MetricBar>
      }
    >
      {/* Shop selector */}
      {shops.length > 1 && (
        <div className="mb-4">
          <FilterDropdown
            label="Select Shop"
            value={selectedShop}
            options={shops.map(s => ({ label: s.shop_name, value: s.id }))}
            onChange={setSelectedShop}
          />
        </div>
      )}

      {/* Conversations list */}
      <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-900">Buyer Conversations</h3>
        </div>
        <div className="divide-y divide-gray-50">
          {conversations.map((conv, i) => (
            <div key={i} className="px-5 py-3 hover:bg-gray-50 cursor-pointer transition-colors">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">
                  {(conv.buyer_name as string) || `Conversation ${i + 1}`}
                </span>
                <span className="text-xs text-gray-400">
                  {conv.last_message_time ? new Date(conv.last_message_time as string).toLocaleDateString() : ""}
                </span>
              </div>
              {conv.last_message ? (
                <p className="text-sm text-gray-500 mt-0.5 truncate">{String(conv.last_message)}</p>
              ) : null}
            </div>
          ))}
          {!loading && conversations.length === 0 && (
            <EmptyState
              icon={MessageSquare}
              title="No conversations found"
              description="Buyer conversations will appear here when customers message your shop."
            />
          )}
        </div>
      </div>

      {loading && <div className="text-center py-8 text-gray-500 text-sm">Loading conversations...</div>}
    </PageShell>
  );
}
