"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getActiveSyncJobs, getMe, type SyncJob } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { useSyncWebSocket, type SyncWSMessage } from "@/hooks/useSyncWebSocket";
import { PageHeader } from "@/components/dashboard/page-header";

interface SyncProgress {
  platform: string;
  sync_type: string;
  items_synced: number;
  items_total: number | null;
  status: "pending" | "running" | "completed" | "failed";
  error?: string;
}

export default function SyncProgressPage() {
  const router = useRouter();
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [progress, setProgress] = useState<Map<string, SyncProgress>>(new Map());
  const token = typeof window !== "undefined" ? getAccessToken() : null;

  useEffect(() => {
    if (!token) return;
    getMe(token).then((user) => {
      if (!user.workspace_id) return;
      setWorkspaceId(user.workspace_id);
      getActiveSyncJobs(user.workspace_id, token).then((jobs: SyncJob[]) => {
        const initial = new Map<string, SyncProgress>();
        for (const job of jobs) {
          initial.set(`${job.platform}:${job.sync_type}`, {
            platform: job.platform,
            sync_type: job.sync_type,
            items_synced: job.items_synced,
            items_total: job.items_total,
            status: job.status,
          });
        }
        setProgress(initial);
      });
    });
  }, [token]);

  useSyncWebSocket({
    workspaceId: workspaceId || "",
    token,
    onMessage: (msg: SyncWSMessage) => {
      const key = `${msg.platform}:${msg.sync_type}`;
      setProgress((prev) => {
        const next = new Map(prev);
        next.set(key, {
          platform: msg.platform,
          sync_type: msg.sync_type,
          items_synced: msg.items_synced,
          items_total: msg.items_total,
          status: msg.type === "sync_complete" ? "completed" : msg.type === "sync_failed" ? "failed" : "running",
          error: msg.error,
        });
        return next;
      });
    },
  });

  const entries = Array.from(progress.values());
  const allCompleted = entries.length > 0 && entries.every((e) => e.status === "completed");
  const hasFailed = entries.some((e) => e.status === "failed");

  return (
    <div>
      <PageHeader
        title="Syncing Your Data"
        description="We're pulling your TikTok data into Frodo. This usually takes a few minutes."
      />

      {entries.length === 0 ? (
        <div className="text-center py-12">
          <div className="animate-spin h-8 w-8 border-2 border-coral border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-gray-500">Waiting for sync to start...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {entries.map((entry) => {
            const pct = entry.items_total
              ? Math.round((entry.items_synced / entry.items_total) * 100)
              : null;

            return (
              <div
                key={`${entry.platform}:${entry.sync_type}`}
                className="bg-white rounded-lg border border-gray-200 p-4"
              >
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <span className="font-medium text-gray-900 capitalize">
                      {entry.platform}
                    </span>
                    <span className="text-gray-400 mx-2">&middot;</span>
                    <span className="text-gray-600 capitalize">
                      {entry.sync_type.replace("_", " ")}
                    </span>
                  </div>
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                      entry.status === "completed"
                        ? "bg-green-100 text-green-700"
                        : entry.status === "failed"
                          ? "bg-red-100 text-red-700"
                          : "bg-blue-100 text-blue-700"
                    }`}
                  >
                    {entry.status === "running" && pct !== null
                      ? `${pct}%`
                      : entry.status}
                  </span>
                </div>

                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${
                      entry.status === "completed"
                        ? "bg-green-500"
                        : entry.status === "failed"
                          ? "bg-red-500"
                          : "bg-coral"
                    }`}
                    style={{ width: `${pct ?? (entry.status === "completed" ? 100 : 10)}%` }}
                  />
                </div>

                <p className="text-xs text-gray-500 mt-1">
                  {entry.items_synced}
                  {entry.items_total ? ` / ${entry.items_total}` : ""} items synced
                </p>

                {entry.error && (
                  <p className="text-xs text-red-600 mt-1">{entry.error}</p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {allCompleted && (
        <div className="mt-8 text-center">
          <p className="text-green-600 font-medium mb-4">All data synced successfully!</p>
          <button
            onClick={() => router.push("/overview")}
            className="bg-coral text-white px-6 py-2.5 rounded-md font-medium hover:bg-coral/90"
          >
            Go to Dashboard
          </button>
        </div>
      )}

      {hasFailed && (
        <div className="mt-6 text-center">
          <p className="text-red-600 text-sm mb-2">Some syncs failed. You can retry from the sync status page.</p>
          <button
            onClick={() => router.push("/connect/status")}
            className="text-coral text-sm font-medium hover:text-coral/80"
          >
            View Sync Status
          </button>
        </div>
      )}
    </div>
  );
}
