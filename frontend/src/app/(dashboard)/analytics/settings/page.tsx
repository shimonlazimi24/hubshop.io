"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Key,
  Plus,
  Trash2,
  Copy,
  Check,
  AlertTriangle,
  Users,
  Shield,
} from "lucide-react";
import { getAccessToken } from "@/lib/auth";
import {
  listApiKeys,
  createApiKey,
  revokeApiKey,
  type ApiKeyItem,
  type ApiKeyCreateResponse,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { Modal } from "@/components/ui/modal";
import { StatusBadge } from "@/components/ui/status-badge";
import { toast } from "@/lib/toast-store";
import { Skeleton } from "@/components/ui/skeleton";
import { useWorkspace } from "@/hooks/useWorkspace";


const SCOPE_OPTIONS = [
  "commerce:read",
  "commerce:write",
  "advertising:read",
  "advertising:write",
  "content:read",
  "content:write",
  "analytics:read",
];

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "\u2014";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatScopes(scopes: Record<string, unknown>): string {
  if (Array.isArray(scopes)) return scopes.join(", ");
  const keys = Object.keys(scopes);
  if (keys.length === 0) return "All";
  return keys.join(", ");
}

export default function SettingsPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const [apiKeys, setApiKeys] = useState<ApiKeyItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [rawKey, setRawKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Create form state
  const [formName, setFormName] = useState("");
  const [formScopes, setFormScopes] = useState<string[]>([]);

  const fetchKeys = useCallback(async () => {
    const token = getAccessToken();
    if (!token || !WORKSPACE_ID) {
      setLoading(false);
      return;
    }
    try {
      const data = await listApiKeys(WORKSPACE_ID, token);
      setApiKeys(data);
    } catch {
      setApiKeys([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchKeys();
  }, [fetchKeys]);

  async function handleCreate() {
    const token = getAccessToken();
    if (!token || !WORKSPACE_ID || !formName.trim()) return;
    setCreating(true);
    try {
      const result: ApiKeyCreateResponse = await createApiKey(
        WORKSPACE_ID,
        {
          name: formName,
          scopes: formScopes.length > 0 ? formScopes : undefined,
        },
        token
      );
      setRawKey(result.raw_key);
      setShowCreate(false);
      resetForm();
      fetchKeys();
      toast.success("API key created successfully");
    } catch {
      toast.error("Failed to create API key");
    } finally {
      setCreating(false);
    }
  }

  function resetForm() {
    setFormName("");
    setFormScopes([]);
  }

  async function handleRevoke(keyId: string) {
    const token = getAccessToken();
    if (!token || !WORKSPACE_ID) return;
    try {
      await revokeApiKey(keyId, token);
      fetchKeys();
      toast.success("API key revoked");
    } catch {
      toast.error("Failed to revoke API key");
    }
  }

  function toggleScope(scope: string) {
    setFormScopes((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope]
    );
  }

  async function copyKey() {
    if (!rawKey) return;
    try {
      await navigator.clipboard.writeText(rawKey);
      setCopied(true);
      toast.success("Key copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Failed to copy to clipboard");
    }
  }

  const activeKeys = apiKeys.filter((k) => k.is_active).length;
  const revokedKeys = apiKeys.filter((k) => !k.is_active).length;

  const columns: Column<ApiKeyItem>[] = [
    {
      key: "name",
      header: "Name",
      render: (row) => (
        <div className="flex items-center gap-2">
          <Shield className={cn("h-3.5 w-3.5", row.is_active ? "text-emerald-500" : "text-gray-300")} />
          <span className="text-sm font-medium text-gray-900">{row.name}</span>
          {!row.is_active && <StatusBadge variant="error" label="Revoked" />}
        </div>
      ),
    },
    {
      key: "prefix",
      header: "Key Prefix",
      render: (row) => (
        <code className="rounded bg-gray-50 px-2 py-0.5 text-xs font-mono text-gray-600">
          {row.key_prefix}...
        </code>
      ),
    },
    {
      key: "scopes",
      header: "Scopes",
      render: (row) => <span className="text-xs text-gray-500">{formatScopes(row.scopes)}</span>,
    },
    {
      key: "created",
      header: "Created",
      render: (row) => <span className="text-xs text-gray-500">{formatDate(row.created_at)}</span>,
    },
    {
      key: "last_used",
      header: "Last Used",
      render: (row) => <span className="text-xs text-gray-500">{formatDate(row.last_used_at)}</span>,
    },
    {
      key: "actions",
      header: "Actions",
      className: "w-20",
      render: (row) => (
        <div className="flex items-center justify-end">
          {row.is_active && (
            <button
              onClick={() => handleRevoke(row.id)}
              className="rounded-lg p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
              title="Revoke"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <PageShell
      header={
        loading ? (
          <MetricBar>
            <Skeleton className="h-16 flex-1 rounded-xl" />
            <Skeleton className="h-16 flex-1 rounded-xl" />
            <Skeleton className="h-16 flex-1 rounded-xl" />
          </MetricBar>
        ) : (
          <MetricBar>
            <MetricCard label="Total Keys" value={apiKeys.length} icon={Key} />
            <MetricCard label="Active" value={activeKeys} icon={Shield} />
            <MetricCard label="Revoked" value={revokedKeys} icon={Trash2} />
          </MetricBar>
        )
      }
      aside={
        <InsightPanel>
          <InsightItem
            title="Security"
            description="API keys provide programmatic access to your workspace. Keep them secret and rotate regularly."
            variant="warning"
          />
          <InsightItem
            title="Scopes"
            description="Limit key permissions using scopes. Use read-only scopes for analytics integrations."
          />
        </InsightPanel>
      }
    >
      {/* Raw Key Warning Banner */}
      {rawKey && (
        <div className="rounded-xl border border-yellow-200 bg-yellow-50 p-4 mb-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-yellow-800">Save your API key now</p>
              <p className="text-xs text-yellow-700 mt-1">
                This is the only time you will see this key. Store it securely -- it cannot be recovered after you dismiss this.
              </p>
              <div className="flex items-center gap-2 mt-3">
                <code className="flex-1 rounded-lg bg-yellow-100 border border-yellow-200 px-3 py-2 text-xs font-mono text-yellow-900 break-all select-all">
                  {rawKey}
                </code>
                <button
                  onClick={copyKey}
                  className="flex items-center gap-1.5 rounded-lg border border-yellow-300 bg-white px-3 py-2 text-xs font-medium text-yellow-700 hover:bg-yellow-50 transition-colors flex-shrink-0"
                >
                  {copied ? (
                    <><Check className="h-3.5 w-3.5" /> Copied</>
                  ) : (
                    <><Copy className="h-3.5 w-3.5" /> Copy</>
                  )}
                </button>
              </div>
              <button
                onClick={() => setRawKey(null)}
                className="mt-3 text-xs text-yellow-600 hover:text-yellow-800 underline"
              >
                I have saved it, dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* API Keys */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Key className="h-4 w-4 text-gray-400" />
          <h3 className="text-sm font-semibold text-gray-900">API Keys</h3>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
        >
          <Plus className="h-3.5 w-3.5" />
          Create API Key
        </button>
      </div>

      <DataTable
        columns={columns}
        data={apiKeys}
        keyExtractor={(row) => row.id}
        emptyTitle="No API keys"
        emptyDescription="Create one to get started with the API"
        emptyAction={{ label: "Create API Key", onClick: () => setShowCreate(true) }}
      />

      {/* Team Management Placeholder */}
      <div className="mt-10">
        <div className="flex items-center gap-2 mb-4">
          <Users className="h-4 w-4 text-gray-400" />
          <h3 className="text-sm font-semibold text-gray-900">Team Management</h3>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)]">
          <div className="flex flex-col items-center justify-center py-12 px-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-50 mb-3">
              <Users className="h-5 w-5 text-gray-300" />
            </div>
            <p className="text-sm text-gray-400">Coming soon</p>
            <p className="text-xs text-gray-300 mt-1">
              Invite team members, manage roles, and control workspace access
            </p>
          </div>
        </div>
      </div>

      {/* Create Modal */}
      <Modal open={showCreate} onClose={() => { setShowCreate(false); resetForm(); }} title="New API Key">
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Name *</label>
            <input
              type="text"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder="My API Key"
              className="w-full max-w-sm rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-coral focus:ring-1 focus:ring-coral outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-2">Scopes</label>
            <div className="flex flex-wrap gap-2">
              {SCOPE_OPTIONS.map((scope) => (
                <button
                  key={scope}
                  onClick={() => toggleScope(scope)}
                  className={cn(
                    "rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors",
                    formScopes.includes(scope)
                      ? "border-coral bg-coral/5 text-coral"
                      : "border-gray-200 text-gray-500 hover:border-gray-300"
                  )}
                >
                  {scope}
                </button>
              ))}
            </div>
            <p className="text-[11px] text-gray-400 mt-2">Leave empty to grant all scopes</p>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              onClick={() => { setShowCreate(false); resetForm(); }}
              className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={!formName.trim() || creating}
              className="rounded-lg bg-coral px-4 py-2 text-sm font-medium text-white hover:bg-coral/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {creating ? "Creating..." : "Create Key"}
            </button>
          </div>
        </div>
      </Modal>
    </PageShell>
  );
}
