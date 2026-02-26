"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import {
  getAuthorizeUrl,
  getMe,
  listConnectedAccounts,
  type ConnectedAccount,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageHeader } from "@/components/dashboard/page-header";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";

const PLATFORMS = [
  {
    id: "shop",
    name: "TikTok Shop",
    description: "Products, orders, fulfillment, returns, finance",
    color: "bg-red-500",
    scopes: "Implicit (all 13 domains)",
  },
  {
    id: "developer",
    name: "TikTok Account",
    description: "Videos, comments, user profile, publishing",
    color: "bg-black",
    scopes: "8 scopes (user, video, comment)",
  },
  {
    id: "marketing",
    name: "TikTok Ads",
    description: "Campaigns, audiences, creatives, reporting",
    color: "bg-blue-500",
    scopes: "Implicit (full Marketing API)",
  },
];

function toStatusVariant(status: string): StatusVariant {
  switch (status) {
    case "active":
      return "active";
    case "expired":
    case "revoked":
      return "error";
    case "syncing":
      return "syncing";
    default:
      return "warning";
  }
}

export default function ConnectPage() {
  const [accounts, setAccounts] = useState<ConnectedAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;

    loadAccounts(token);
  }, []);

  async function loadAccounts(token: string) {
    try {
      const user = await getMe(token);
      const wsId = user.workspace_id;
      if (!wsId) return;
      setWorkspaceId(wsId);
      const accts = await listConnectedAccounts(wsId, token);
      setAccounts(accts);
    } catch {
      toast.error("Failed to load connected accounts");
    } finally {
      setLoading(false);
    }
  }

  async function handleConnect(platform: string) {
    const token = getAccessToken();
    if (!token || !workspaceId) return;

    try {
      const { authorize_url } = await getAuthorizeUrl(platform, workspaceId, token);
      window.location.href = authorize_url;
    } catch (err) {
      toast.error(
        `Failed to start connection: ${err instanceof Error ? err.message : "Unknown error"}`
      );
    }
  }

  const connectedPlatforms = new Map(accounts.map((a) => [a.platform, a]));

  if (loading) {
    return (
      <div>
        <PageHeader title="Connect" description="Link your TikTok platform accounts." />
        <div className="flex justify-center py-12">
          <div className="animate-spin h-8 w-8 border-2 border-coral border-t-transparent rounded-full" />
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Connect"
        description="Link your TikTok platform accounts to manage everything from one place."
      />

      <div className="flex items-center justify-between mb-6">
        <p className="text-sm text-gray-500">
          {accounts.length} of {PLATFORMS.length} platforms connected
        </p>
        <Link
          href="/connect/status"
          className="text-sm text-coral hover:text-coral/80 font-medium"
        >
          View Sync Status &rarr;
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {PLATFORMS.map((platform) => {
          const account = connectedPlatforms.get(platform.id);
          const isConnected = !!account;
          return (
            <div
              key={platform.id}
              className="bg-white rounded-lg border border-gray-200 p-6 flex flex-col"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-10 h-10 ${platform.color} rounded-lg`} />
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{platform.name}</h3>
                </div>
                {account && (
                  <StatusBadge variant={toStatusVariant(account.status)} />
                )}
              </div>

              <p className="text-sm text-gray-500 flex-1">{platform.description}</p>

              {account && (
                <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600">
                  <p className="font-medium">
                    {account.platform_account_name || account.platform_account_id}
                  </p>
                  <p className="text-gray-400 mt-0.5">Scopes: {platform.scopes}</p>
                </div>
              )}

              <button
                onClick={() => handleConnect(platform.id)}
                className={`mt-4 w-full py-2.5 px-4 rounded-md text-sm font-medium transition-colors ${
                  isConnected
                    ? "bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100"
                    : "bg-coral text-white hover:bg-coral/90"
                }`}
              >
                {isConnected ? "Reconnect" : "Connect"}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
