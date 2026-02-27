"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { MessageSquare, Mail, Bot, TrendingUp, Clock, User, ArrowRight, RefreshCw } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { EmptyState } from "@/components/ui/empty-state";
import { toast } from "@/lib/toast-store";
import { listMessagingConversations, listConnectedAccounts } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { useWorkspace } from "@/hooks/useWorkspace";
import { cn } from "@/lib/utils";

interface Conversation {
  id: string;
  userName: string;
  lastMessage: string;
  timestamp: string;
  unread: number;
  status: "active" | "resolved" | "waiting";
}

const STATUS_MAP: Record<string, StatusVariant> = {
  active: "active",
  resolved: "completed",
  waiting: "warning",
};

function formatTime(ts: string): string {
  const date = new Date(ts);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 1) return "Just now";
  if (hours < 24) return `${hours}h ago`;
  return date.toLocaleDateString();
}

function mapConversation(raw: Record<string, unknown>): Conversation {
  return {
    id: String(raw.id || raw.tiktok_conversation_id || ""),
    userName: String(raw.participant_display_name || raw.user_display_name || "Unknown"),
    lastMessage: String(raw.last_message || raw.last_message_content || ""),
    timestamp: String(raw.last_message_at || raw.updated_at || new Date().toISOString()),
    unread: Number(raw.unread_count || 0),
    status: raw.status === "ARCHIVED" ? "resolved" : raw.unread_count ? "active" : "waiting",
  };
}

export default function MessagingOverviewPage() {
  const { workspaceId } = useWorkspace();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [connectedAccountId, setConnectedAccountId] = useState<string | null>(null);

  const token = getAccessToken();

  useEffect(() => {
    if (!token || !workspaceId) return;
    listConnectedAccounts(workspaceId, token)
      .then((accounts) => {
        const marketingAccount = accounts.find((a) => a.platform === "marketing");
        if (marketingAccount) setConnectedAccountId(marketingAccount.id);
      })
      .catch(console.error);
  }, [token, workspaceId]);

  useEffect(() => {
    loadConversations();
  }, [connectedAccountId]);

  function loadConversations() {
    if (!token || !connectedAccountId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    listMessagingConversations(connectedAccountId, token)
      .then((data) => {
        setConversations((data.conversations || []).map(mapConversation));
      })
      .catch((err) => {
        console.error(err);
        toast.error("Failed to load conversations");
      })
      .finally(() => setLoading(false));
  }

  const filtered = conversations.filter((c) => {
    if (search && !c.userName.toLowerCase().includes(search.toLowerCase())) return false;
    if (statusFilter && c.status !== statusFilter) return false;
    return true;
  });

  const activeCount = conversations.filter((c) => c.status === "active").length;
  const unreadTotal = conversations.reduce((sum, c) => sum + c.unread, 0);

  const columns: Column<Conversation>[] = [
    {
      key: "user",
      header: "Customer",
      render: (row) => (
        <Link href={`/messaging/${row.id}?account=${connectedAccountId}`} className="flex items-center gap-3 group">
          <div className={cn(
            "flex h-9 w-9 items-center justify-center rounded-full flex-shrink-0",
            row.status === "active" ? "bg-purple/10" : row.status === "waiting" ? "bg-yellow-50" : "bg-gray-100"
          )}>
            <User className={cn("h-4 w-4", row.status === "active" ? "text-purple" : row.status === "waiting" ? "text-yellow-500" : "text-gray-400")} />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium text-gray-900 group-hover:text-coral transition-colors">{row.userName}</p>
              {row.unread > 0 && (
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-coral text-[10px] font-semibold text-white">{row.unread}</span>
              )}
            </div>
            <p className="text-xs text-gray-500 truncate max-w-sm">{row.lastMessage}</p>
          </div>
        </Link>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (row) => <StatusBadge variant={STATUS_MAP[row.status] || "draft"} label={row.status} />,
    },
    {
      key: "time",
      header: "Time",
      render: (row) => (
        <span className="text-xs text-gray-400 flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {formatTime(row.timestamp)}
        </span>
      ),
    },
    {
      key: "action",
      header: "",
      className: "w-10",
      render: (row) => (
        <Link href={`/messaging/${row.id}?account=${connectedAccountId}`}>
          <ArrowRight className="h-4 w-4 text-gray-300 hover:text-gray-500 transition-colors" />
        </Link>
      ),
    },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Active Conversations" value={activeCount} icon={MessageSquare} />
          <MetricCard label="Unread Messages" value={unreadTotal} icon={Mail} />
          <MetricCard label="Total Conversations" value={conversations.length} icon={Bot} />
          <MetricCard label="Response Rate" value={conversations.length ? "—" : "—"} icon={TrendingUp} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Response time" description="Average first response time is calculated from your conversation data. Keep it under 15 minutes for best satisfaction." variant="success" />
          <InsightItem title="Unread messages" description={`${unreadTotal} unread messages across ${conversations.filter((c) => c.unread > 0).length} conversations.`} variant={unreadTotal > 5 ? "warning" : "default"} />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search conversations..."
        actions={
          <button onClick={loadConversations} disabled={loading} className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50">
            <RefreshCw className={cn("h-3.5 w-3.5", loading && "animate-spin")} />
            Refresh
          </button>
        }
      >
        <FilterDropdown
          label="Status"
          value={statusFilter}
          onChange={setStatusFilter}
          options={[
            { label: "Active", value: "active" },
            { label: "Waiting", value: "waiting" },
            { label: "Resolved", value: "resolved" },
          ]}
        />
      </FilterBar>

      {!connectedAccountId && !loading ? (
        <EmptyState
          icon={MessageSquare}
          title="No Marketing Account Connected"
          description="Connect your TikTok Marketing account to access business messaging."
        />
      ) : (
        <DataTable
          columns={columns}
          data={filtered}
          keyExtractor={(row) => row.id}
          loading={loading}
          emptyTitle="No conversations"
          emptyDescription="Customer conversations will appear here once you receive messages"
        />
      )}
    </PageShell>
  );
}
