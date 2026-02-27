"use client";

import { useEffect, useState } from "react";
import { Bot, MessageCircle, HelpCircle, Megaphone, RefreshCw } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { EmptyState } from "@/components/ui/empty-state";
import { Modal } from "@/components/ui/modal";
import { toast } from "@/lib/toast-store";
import { listAutoMessages, createAutoMessage, toggleAutoMessage, deleteAutoMessage, listConnectedAccounts } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { useWorkspace } from "@/hooks/useWorkspace";
import { cn } from "@/lib/utils";

type TabType = "WELCOME" | "SUGGESTED_QUESTION" | "CHAT_PROMPT";

interface AutoMessageItem {
  id: string;
  messageType: string;
  content: string;
  isActive: boolean;
}

const STATUS_VARIANT: Record<string, StatusVariant> = { true: "active", false: "paused" };

function mapAutoMessage(raw: Record<string, unknown>): AutoMessageItem {
  return {
    id: String(raw.id || raw.tiktok_auto_message_id || ""),
    messageType: String(raw.message_type || "WELCOME"),
    content: String(raw.content || ""),
    isActive: Boolean(raw.is_active ?? raw.enabled ?? true),
  };
}

export default function AutoMessagesPage() {
  const { workspaceId } = useWorkspace();
  const [tab, setTab] = useState<TabType>("WELCOME");
  const [autoMessages, setAutoMessages] = useState<AutoMessageItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [createContent, setCreateContent] = useState("");
  const [creating, setCreating] = useState(false);
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
    loadAutoMessages();
  }, [connectedAccountId]);

  function loadAutoMessages() {
    if (!token || !connectedAccountId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    listAutoMessages(connectedAccountId, token)
      .then((data) => {
        setAutoMessages((data.auto_messages || []).map(mapAutoMessage));
      })
      .catch((err) => {
        console.error(err);
        toast.error("Failed to load auto-messages");
      })
      .finally(() => setLoading(false));
  }

  const filtered = autoMessages.filter((m) => m.messageType === tab);

  async function handleCreate() {
    if (!token || !connectedAccountId || !createContent.trim()) return;
    setCreating(true);
    try {
      await createAutoMessage(connectedAccountId, tab, createContent.trim(), token);
      toast.success("Auto-message created");
      setShowCreate(false);
      setCreateContent("");
      loadAutoMessages();
    } catch {
      toast.error("Failed to create auto-message");
    } finally {
      setCreating(false);
    }
  }

  async function handleToggle(item: AutoMessageItem) {
    if (!token || !connectedAccountId) return;
    try {
      await toggleAutoMessage(item.id, connectedAccountId, !item.isActive, token);
      toast.success(item.isActive ? "Auto-message paused" : "Auto-message activated");
      loadAutoMessages();
    } catch {
      toast.error("Failed to toggle auto-message");
    }
  }

  async function handleDelete(item: AutoMessageItem) {
    if (!token || !connectedAccountId) return;
    try {
      await deleteAutoMessage(item.id, connectedAccountId, token);
      toast.success("Auto-message deleted");
      loadAutoMessages();
    } catch {
      toast.error("Failed to delete auto-message");
    }
  }

  const columns: Column<AutoMessageItem>[] = [
    {
      key: "content",
      header: "Content",
      render: (row) => (
        <div>
          <p className="text-sm text-gray-900 bg-gray-50 rounded-lg px-3 py-2">{row.content}</p>
        </div>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (row) => <StatusBadge variant={STATUS_VARIANT[String(row.isActive)] || "draft"} label={row.isActive ? "Active" : "Paused"} />,
    },
    {
      key: "actions",
      header: "",
      className: "w-32",
      render: (row) => (
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleToggle(row)}
            className="px-2.5 py-1 text-xs font-medium rounded-md bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
          >
            {row.isActive ? "Pause" : "Activate"}
          </button>
          <button
            onClick={() => handleDelete(row)}
            className="px-2.5 py-1 text-xs font-medium rounded-md bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
          >
            Delete
          </button>
        </div>
      ),
    },
  ];

  const tabConfig = [
    { key: "WELCOME" as const, label: "Welcome Messages", icon: MessageCircle },
    { key: "SUGGESTED_QUESTION" as const, label: "Suggested Questions", icon: HelpCircle },
    { key: "CHAT_PROMPT" as const, label: "Chat Prompts", icon: Megaphone },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Total Auto-Messages" value={autoMessages.length} icon={Bot} />
          <MetricCard label="Active" value={autoMessages.filter((m) => m.isActive).length} icon={MessageCircle} />
          <MetricCard label="Welcome" value={autoMessages.filter((m) => m.messageType === "WELCOME").length} icon={MessageCircle} />
          <MetricCard label="Prompts" value={autoMessages.filter((m) => m.messageType === "CHAT_PROMPT").length} icon={Megaphone} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Auto-messages" description="Auto-messages are managed via the TikTok Business Messaging API. Changes sync in real-time." variant="default" />
        </InsightPanel>
      }
    >
      {!connectedAccountId && !loading ? (
        <EmptyState
          icon={Bot}
          title="No Marketing Account Connected"
          description="Connect your TikTok Marketing account to manage auto-messages."
        />
      ) : (
        <>
          <div className="flex items-center justify-between mb-4">
            <div className="flex gap-2">
              {tabConfig.map((t) => (
                <button
                  key={t.key}
                  onClick={() => setTab(t.key)}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors",
                    tab === t.key ? "bg-gray-900 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  )}
                >
                  <t.icon className="h-3.5 w-3.5" />
                  {t.label}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <button onClick={loadAutoMessages} disabled={loading} className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50">
                <RefreshCw className={cn("h-3.5 w-3.5", loading && "animate-spin")} />
              </button>
              <button onClick={() => setShowCreate(true)} className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 transition-colors">
                Add New
              </button>
            </div>
          </div>

          <DataTable
            columns={columns}
            data={filtered}
            keyExtractor={(row) => row.id}
            loading={loading}
            emptyTitle={`No ${tab.toLowerCase().replace("_", " ")}s`}
            emptyDescription={`Create a ${tab.toLowerCase().replace("_", " ")} to get started`}
          />
        </>
      )}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title={`New ${tab === "WELCOME" ? "Welcome Message" : tab === "SUGGESTED_QUESTION" ? "Suggested Question" : "Chat Prompt"}`}>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Content *</label>
            <textarea
              value={createContent}
              onChange={(e) => setCreateContent(e.target.value)}
              placeholder="Message content..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none resize-none"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button onClick={() => setShowCreate(false)} className="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50">Cancel</button>
            <button onClick={handleCreate} disabled={!createContent.trim() || creating} className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 disabled:opacity-50">
              {creating ? "Creating..." : "Create"}
            </button>
          </div>
        </div>
      </Modal>
    </PageShell>
  );
}
