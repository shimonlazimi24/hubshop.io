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
  X,
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
import { Skeleton } from "@/components/ui/skeleton";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

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

export default function SettingsPage() {
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
    if (!token) {
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
    if (!token || !formName.trim()) return;
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
    } catch {
      // Keep form open on error
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
    if (!token) return;
    try {
      await revokeApiKey(keyId, token);
      fetchKeys();
    } catch {
      // Silent fail
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
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard access denied
    }
  }

  function formatScopes(scopes: Record<string, unknown>): string {
    if (Array.isArray(scopes)) return scopes.join(", ");
    const keys = Object.keys(scopes);
    if (keys.length === 0) return "All";
    return keys.join(", ");
  }

  return (
    <div className="max-w-6xl">
      {/* Raw Key Warning Banner */}
      {rawKey && (
        <div className="rounded-xl border border-yellow-200 bg-yellow-50 p-4 mb-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-yellow-800">
                Save your API key now
              </p>
              <p className="text-xs text-yellow-700 mt-1">
                This is the only time you will see this key. Store it securely
                -- it cannot be recovered after you dismiss this.
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
                    <>
                      <Check className="h-3.5 w-3.5" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5" />
                      Copy
                    </>
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

      {/* API Keys Section */}
      <div className="mb-10">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Key className="h-4 w-4 text-gray-400" />
            <h2 className="text-sm font-semibold text-gray-900">API Keys</h2>
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
          >
            <Plus className="h-3.5 w-3.5" />
            Create API Key
          </button>
        </div>

        {/* Create Form */}
        {showCreate && (
          <div className="rounded-xl border border-gray-200 bg-white p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-900">
                New API Key
              </h3>
              <button
                onClick={() => {
                  setShowCreate(false);
                  resetForm();
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="mb-4">
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Name *
              </label>
              <input
                type="text"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="My API Key"
                className="w-full max-w-sm rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-coral focus:ring-1 focus:ring-coral outline-none"
              />
            </div>

            <div className="mb-6">
              <label className="block text-xs font-medium text-gray-500 mb-2">
                Scopes
              </label>
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
              <p className="text-[11px] text-gray-400 mt-2">
                Leave empty to grant all scopes
              </p>
            </div>

            <div className="flex justify-end gap-2">
              <button
                onClick={() => {
                  setShowCreate(false);
                  resetForm();
                }}
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
        )}

        {/* API Keys Table */}
        <div className="rounded-xl border border-gray-100 bg-white overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left text-xs font-medium text-gray-400 px-4 py-3">
                    Name
                  </th>
                  <th className="text-left text-xs font-medium text-gray-400 px-4 py-3">
                    Key Prefix
                  </th>
                  <th className="text-left text-xs font-medium text-gray-400 px-4 py-3">
                    Scopes
                  </th>
                  <th className="text-left text-xs font-medium text-gray-400 px-4 py-3">
                    Created
                  </th>
                  <th className="text-left text-xs font-medium text-gray-400 px-4 py-3">
                    Last Used
                  </th>
                  <th className="text-right text-xs font-medium text-gray-400 px-4 py-3">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  Array.from({ length: 2 }).map((_, i) => (
                    <tr key={i} className="border-b border-gray-50">
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-32" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-24" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-40" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-20" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-20" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-8 ml-auto" />
                      </td>
                    </tr>
                  ))
                ) : apiKeys.length === 0 ? (
                  <tr>
                    <td
                      colSpan={6}
                      className="px-4 py-12 text-center text-sm text-gray-400"
                    >
                      No API keys yet. Create one to get started.
                    </td>
                  </tr>
                ) : (
                  apiKeys.map((key) => (
                    <tr
                      key={key.id}
                      className={cn(
                        "border-b border-gray-50 hover:bg-gray-50/50 transition-colors",
                        !key.is_active && "opacity-50"
                      )}
                    >
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <Shield
                            className={cn(
                              "h-3.5 w-3.5",
                              key.is_active
                                ? "text-emerald-500"
                                : "text-gray-300"
                            )}
                          />
                          <span className="text-sm font-medium text-gray-900">
                            {key.name}
                          </span>
                          {!key.is_active && (
                            <span className="inline-flex items-center rounded-md bg-red-50 px-1.5 py-0.5 text-[10px] font-medium text-red-600">
                              Revoked
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <code className="rounded bg-gray-50 px-2 py-0.5 text-xs font-mono text-gray-600">
                          {key.key_prefix}...
                        </code>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs text-gray-500">
                          {formatScopes(key.scopes)}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs text-gray-500">
                          {formatDate(key.created_at)}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs text-gray-500">
                          {formatDate(key.last_used_at)}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end">
                          {key.is_active && (
                            <button
                              onClick={() => handleRevoke(key.id)}
                              className="rounded-lg p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                              title="Revoke"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Team Management Placeholder */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Users className="h-4 w-4 text-gray-400" />
          <h2 className="text-sm font-semibold text-gray-900">
            Team Management
          </h2>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white">
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
    </div>
  );
}
