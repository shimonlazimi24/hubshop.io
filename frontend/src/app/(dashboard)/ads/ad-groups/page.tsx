"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  listAdAccounts,
  listAdGroups,
  syncAdGroups,
  type AdAccount,
  type AdGroupSummary,
  type PaginatedResponse,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_COLORS: Record<string, string> = {
  ENABLE: "bg-green-100 text-green-800",
  DISABLE: "bg-gray-100 text-gray-800",
  DELETE: "bg-red-100 text-red-800",
};

export default function AdGroupsPage() {
  const [adGroups, setAdGroups] = useState<PaginatedResponse<AdGroupSummary> | null>(null);
  const [adAccounts, setAdAccounts] = useState<AdAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");
  const [accountFilter, setAccountFilter] = useState("");
  const [page, setPage] = useState(1);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    listAdAccounts(WORKSPACE_ID, token).then(setAdAccounts).catch(console.error);
  }, []);

  useEffect(() => {
    loadAdGroups();
  }, [statusFilter, accountFilter, page]);

  function loadAdGroups() {
    if (!token) return;
    setLoading(true);
    listAdGroups(WORKSPACE_ID, token, {
      status_filter: statusFilter || undefined,
      ad_account_id: accountFilter || undefined,
      page,
    })
      .then(setAdGroups)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleSync() {
    if (!token) return;
    setSyncing(true);
    try {
      const result = await syncAdGroups(WORKSPACE_ID, token, accountFilter || undefined);
      alert(`Synced ${result.synced} ad groups`);
      loadAdGroups();
    } catch (err) {
      console.error(err);
    } finally {
      setSyncing(false);
    }
  }

  return (
    <div>
      <div className="flex items-center gap-4 mb-4">
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm"
        >
          <option value="">All Statuses</option>
          <option value="ENABLE">Enabled</option>
          <option value="DISABLE">Disabled</option>
        </select>
        {adAccounts.length > 1 && (
          <select
            value={accountFilter}
            onChange={(e) => { setAccountFilter(e.target.value); setPage(1); }}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">All Accounts</option>
            {adAccounts.map((a) => (
              <option key={a.id} value={a.id}>{a.advertiser_name}</option>
            ))}
          </select>
        )}
        <div className="flex-1" />
        <button
          onClick={handleSync}
          disabled={syncing}
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {syncing ? "Syncing..." : "Sync Ad Groups"}
        </button>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Ad Group</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Bid</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Budget</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Goal</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Updated</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {adGroups?.items.map((ag) => (
              <tr key={ag.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <Link
                    href={`/ads/ad-groups/${ag.id}`}
                    className="text-sm font-medium text-blue-600 hover:underline"
                  >
                    {ag.adgroup_name}
                  </Link>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${STATUS_COLORS[ag.operation_status] || "bg-gray-100 text-gray-800"}`}>
                    {ag.operation_status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-900">
                  {ag.bid_amount ? `$${ag.bid_amount}` : "-"}
                  {ag.bid_type && <span className="text-xs text-gray-400 ml-1">({ag.bid_type})</span>}
                </td>
                <td className="px-4 py-3 text-sm text-gray-900">
                  {ag.budget ? `$${ag.budget}` : "-"}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {ag.optimization_goal?.replace(/_/g, " ") || "-"}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {new Date(ag.updated_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
            {!loading && adGroups?.items.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  No ad groups found
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {adGroups && adGroups.total_pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Page {adGroups.page} of {adGroups.total_pages} ({adGroups.total} total)
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => Math.min(adGroups.total_pages, p + 1))}
                disabled={page >= adGroups.total_pages}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Loading ad groups...</div>}
    </div>
  );
}
