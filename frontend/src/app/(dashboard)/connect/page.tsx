"use client";

import { useEffect, useState } from "react";

import {
  getAuthorizeUrl,
  listConnectedAccounts,
  type ConnectedAccount,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const PLATFORMS = [
  {
    id: "shop",
    name: "TikTok Shop",
    description: "Manage products, orders, and fulfillment",
    color: "bg-red-500",
  },
  {
    id: "developer",
    name: "TikTok Developer",
    description: "Access video data and content APIs",
    color: "bg-black",
  },
  {
    id: "marketing",
    name: "TikTok Marketing",
    description: "Manage ad campaigns and audiences",
    color: "bg-blue-500",
  },
];

export default function ConnectPage() {
  const [accounts, setAccounts] = useState<ConnectedAccount[]>([]);
  const [loading, setLoading] = useState(true);

  // TODO: Get workspace ID from context/store
  const workspaceId = "00000000-0000-0000-0000-000000000000";

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;

    listConnectedAccounts(workspaceId, token)
      .then(setAccounts)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  async function handleConnect(platform: string) {
    const token = getAccessToken();
    if (!token) return;

    try {
      const { authorize_url } = await getAuthorizeUrl(platform, workspaceId, token);
      window.location.href = authorize_url;
    } catch (err) {
      console.error("Failed to get authorize URL:", err);
    }
  }

  const connectedPlatforms = new Set(accounts.map((a) => a.platform));

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Connect Accounts</h2>
      <p className="text-gray-500 mb-8">
        Link your TikTok platform accounts to manage everything from one place.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {PLATFORMS.map((platform) => {
          const isConnected = connectedPlatforms.has(platform.id);
          return (
            <div
              key={platform.id}
              className="bg-white rounded-lg border border-gray-200 p-6 flex flex-col"
            >
              <div className={`w-10 h-10 ${platform.color} rounded-lg mb-4`} />
              <h3 className="text-lg font-semibold text-gray-900">{platform.name}</h3>
              <p className="text-sm text-gray-500 mt-1 flex-1">{platform.description}</p>
              <button
                onClick={() => handleConnect(platform.id)}
                disabled={isConnected}
                className={`mt-4 w-full py-2 px-4 rounded-md text-sm font-medium ${
                  isConnected
                    ? "bg-green-50 text-green-700 border border-green-200"
                    : "bg-blue-600 text-white hover:bg-blue-700"
                }`}
              >
                {isConnected ? "Connected" : "Connect"}
              </button>
            </div>
          );
        })}
      </div>

      {/* Connected Accounts List */}
      {accounts.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <h3 className="font-semibold text-gray-900">Connected Accounts</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {accounts.map((account) => (
              <div key={account.id} className="p-4 flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">
                    {account.platform_account_name || account.platform_account_id}
                  </p>
                  <p className="text-sm text-gray-500">{account.platform}</p>
                </div>
                <span
                  className={`px-2 py-1 text-xs rounded-full ${
                    account.status === "active"
                      ? "bg-green-100 text-green-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {account.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading && <p className="text-gray-500 text-center">Loading accounts...</p>}
    </div>
  );
}
