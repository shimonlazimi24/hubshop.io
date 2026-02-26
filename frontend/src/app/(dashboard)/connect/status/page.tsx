"use client";

import { useEffect, useState } from "react";

import {
  getMe,
  listSyncJobs,
  triggerManualSync,
  type SyncJob,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageHeader } from "@/components/dashboard/page-header";

const PLATFORM_LABELS: Record<string, string> = {
  shop: "TikTok Shop",
  developer: "TikTok Account",
  marketing: "TikTok Ads",
};

export default function SyncStatusPage() {
  const [jobs, setJobs] = useState<SyncJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState<string | null>(null);
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);

  useEffect(() => {
    loadJobs();
  }, []);

  async function loadJobs() {
    const token = getAccessToken();
    if (!token) return;

    try {
      const user = await getMe(token);
      if (!user.workspace_id) return;
      setWorkspaceId(user.workspace_id);
      const data = await listSyncJobs(user.workspace_id, token, 50);
      setJobs(data);
    } catch {
      toast.error("Failed to load sync history");
    } finally {
      setLoading(false);
    }
  }

  async function handleSyncNow(platform: string) {
    const token = getAccessToken();
    if (!token || !workspaceId) return;

    setSyncing(platform);
    try {
      await triggerManualSync(workspaceId, platform, token);
      toast.success(`Sync triggered for ${PLATFORM_LABELS[platform] ?? platform}`);
      setTimeout(loadJobs, 2000);
    } catch (err) {
      toast.error(`Failed to trigger sync: ${err instanceof Error ? err.message : "Unknown error"}`);
    } finally {
      setSyncing(null);
    }
  }

  const latestByPlatform = new Map<string, SyncJob>();
  for (const job of jobs) {
    if (!latestByPlatform.has(job.platform)) {
      latestByPlatform.set(job.platform, job);
    }
  }

  return (
    <div>
      <PageHeader title="Sync Status" description="Monitor data sync health across all connected platforms." />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {["shop", "developer", "marketing"].map((platform) => {
          const latest = latestByPlatform.get(platform);
          return (
            <div key={platform} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-900">
                  {PLATFORM_LABELS[platform]}
                </h3>
                {latest && (
                  <span
                    className={`px-2 py-0.5 text-xs rounded-full font-medium ${
                      latest.status === "completed"
                        ? "bg-green-100 text-green-700"
                        : latest.status === "failed"
                          ? "bg-red-100 text-red-700"
                          : latest.status === "running"
                            ? "bg-blue-100 text-blue-700"
                            : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {latest.status}
                  </span>
                )}
              </div>
              {latest ? (
                <div className="text-xs text-gray-500 space-y-1">
                  <p>Last sync: {latest.completed_at ? new Date(latest.completed_at).toLocaleString() : "In progress"}</p>
                  <p>Items: {latest.items_synced}{latest.items_total ? ` / ${latest.items_total}` : ""}</p>
                  {latest.error_message && (
                    <p className="text-red-600">{latest.error_message}</p>
                  )}
                </div>
              ) : (
                <p className="text-xs text-gray-400">No sync history</p>
              )}
              <button
                onClick={() => handleSyncNow(platform)}
                disabled={syncing === platform}
                className="mt-3 w-full py-1.5 px-3 text-xs font-medium rounded-md border border-gray-200 text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                {syncing === platform ? "Syncing..." : "Sync Now"}
              </button>
            </div>
          );
        })}
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">Sync History</h3>
          <button
            onClick={loadJobs}
            className="text-xs text-coral hover:text-coral/80 font-medium"
          >
            Refresh
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin h-6 w-6 border-2 border-coral border-t-transparent rounded-full" />
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-sm">
            No sync jobs yet. Connect a platform to get started.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
                <tr>
                  <th className="px-4 py-2 text-left">Platform</th>
                  <th className="px-4 py-2 text-left">Type</th>
                  <th className="px-4 py-2 text-left">Status</th>
                  <th className="px-4 py-2 text-right">Items</th>
                  <th className="px-4 py-2 text-left">Started</th>
                  <th className="px-4 py-2 text-left">Completed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 font-medium text-gray-900">
                      {PLATFORM_LABELS[job.platform] ?? job.platform}
                    </td>
                    <td className="px-4 py-2 text-gray-600 capitalize">
                      {job.sync_type.replace("_", " ")}
                    </td>
                    <td className="px-4 py-2">
                      <span
                        className={`px-2 py-0.5 text-xs rounded-full font-medium ${
                          job.status === "completed"
                            ? "bg-green-100 text-green-700"
                            : job.status === "failed"
                              ? "bg-red-100 text-red-700"
                              : job.status === "running"
                                ? "bg-blue-100 text-blue-700"
                                : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {job.status}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-right text-gray-600">
                      {job.items_synced}
                      {job.items_total ? ` / ${job.items_total}` : ""}
                    </td>
                    <td className="px-4 py-2 text-gray-500 text-xs">
                      {job.started_at ? new Date(job.started_at).toLocaleString() : "\u2014"}
                    </td>
                    <td className="px-4 py-2 text-gray-500 text-xs">
                      {job.completed_at ? new Date(job.completed_at).toLocaleString() : "\u2014"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
