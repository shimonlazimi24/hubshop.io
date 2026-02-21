"use client";

import { useState } from "react";
import Link from "next/link";
import { MessageSquare, Mail, Bot, TrendingUp, Clock, User, ArrowRight } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { cn } from "@/lib/utils";

interface Conversation {
  id: string;
  userName: string;
  lastMessage: string;
  timestamp: string;
  unread: number;
  status: "active" | "resolved" | "waiting";
}

const MOCK_CONVERSATIONS: Conversation[] = [
  { id: "conv-1", userName: "Sarah Johnson", lastMessage: "When will my order ship? I placed it 3 days ago.", timestamp: "2026-02-20T10:15:00Z", unread: 2, status: "active" },
  { id: "conv-2", userName: "Mike Chen", lastMessage: "Thanks for the quick response! The product is amazing.", timestamp: "2026-02-20T09:45:00Z", unread: 0, status: "resolved" },
  { id: "conv-3", userName: "Emma Wilson", lastMessage: "Do you have this in size M? The listing shows out of stock.", timestamp: "2026-02-20T09:30:00Z", unread: 1, status: "active" },
  { id: "conv-4", userName: "Alex Rivera", lastMessage: "I'd like to return this item. How do I start the process?", timestamp: "2026-02-20T08:20:00Z", unread: 3, status: "waiting" },
  { id: "conv-5", userName: "Lisa Park", lastMessage: "Can you send me more product photos before I buy?", timestamp: "2026-02-20T07:55:00Z", unread: 1, status: "active" },
  { id: "conv-6", userName: "James Taylor", lastMessage: "The discount code doesn't seem to work. Can you help?", timestamp: "2026-02-19T22:30:00Z", unread: 0, status: "resolved" },
  { id: "conv-7", userName: "Nina Patel", lastMessage: "Is this product available for international shipping?", timestamp: "2026-02-19T21:15:00Z", unread: 2, status: "waiting" },
  { id: "conv-8", userName: "David Kim", lastMessage: "Love your store! Do you have a loyalty program?", timestamp: "2026-02-19T20:00:00Z", unread: 0, status: "resolved" },
];

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

export default function MessagingOverviewPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const filtered = MOCK_CONVERSATIONS.filter((c) => {
    if (search && !c.userName.toLowerCase().includes(search.toLowerCase())) return false;
    if (statusFilter && c.status !== statusFilter) return false;
    return true;
  });

  const activeCount = MOCK_CONVERSATIONS.filter((c) => c.status === "active").length;
  const unreadTotal = MOCK_CONVERSATIONS.reduce((sum, c) => sum + c.unread, 0);

  const columns: Column<Conversation>[] = [
    {
      key: "user",
      header: "Customer",
      render: (row) => (
        <Link href={`/messaging/${row.id}`} className="flex items-center gap-3 group">
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
        <Link href={`/messaging/${row.id}`}>
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
          <MetricCard label="Messages Today" value={156} icon={Mail} trend={{ value: 12, direction: "up" }} />
          <MetricCard label="Auto-Messages" value={89} icon={Bot} />
          <MetricCard label="Response Rate" value="94%" icon={TrendingUp} trend={{ value: 94, direction: "up" }} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Response time" description="Average first response time is 4 minutes. Keep it under 15 minutes for best satisfaction." variant="success" />
          <InsightItem title="Unread messages" description={`${unreadTotal} unread messages across ${MOCK_CONVERSATIONS.filter((c) => c.unread > 0).length} conversations. Prioritize waiting customers.`} variant={unreadTotal > 5 ? "warning" : "default"} />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search conversations..."
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

      <DataTable
        columns={columns}
        data={filtered}
        keyExtractor={(row) => row.id}
        emptyTitle="No conversations"
        emptyDescription="Customer conversations will appear here"
      />
    </PageShell>
  );
}
