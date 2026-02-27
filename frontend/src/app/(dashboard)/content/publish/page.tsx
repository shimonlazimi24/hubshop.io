"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Upload, ArrowRight, Clock, CheckCircle } from "lucide-react";
import {
  publishVideo,
  listPublishJobs,
  getCreatorInfo,
  type PublishJob,
  type CreatorInfo,
  type PaginatedResponse,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { toast } from "@/lib/toast-store";
import { useWorkspace } from "@/hooks/useWorkspace";


const STATUS_MAP: Record<string, StatusVariant> = {
  PENDING: "warning",
  PROCESSING: "syncing",
  PUBLISHED: "completed",
  FAILED: "error",
};

const columns: Column<PublishJob>[] = [
  {
    key: "title",
    header: "Title",
    render: (row) => (
      <span className="text-sm font-medium text-gray-900">{row.title || "Untitled"}</span>
    ),
  },
  {
    key: "status",
    header: "Status",
    render: (row) => (
      <StatusBadge variant={STATUS_MAP[row.status] || "draft"} label={row.status} />
    ),
  },
  {
    key: "privacy",
    header: "Privacy",
    render: (row) => (
      <span className="text-sm text-gray-600">{row.privacy_level.replace(/_/g, " ")}</span>
    ),
  },
  {
    key: "created",
    header: "Created",
    render: (row) => (
      <span className="text-sm text-gray-500">{new Date(row.created_at).toLocaleDateString()}</span>
    ),
  },
];

export default function PublishPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const [creatorInfo, setCreatorInfo] = useState<CreatorInfo | null>(null);
  const [jobs, setJobs] = useState<PaginatedResponse<PublishJob> | null>(null);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");
  const [title, setTitle] = useState("");
  const [privacyLevel, setPrivacyLevel] = useState("PUBLIC_TO_EVERYONE");

  const token = getAccessToken();

  useEffect(() => {
    if (!token || !WORKSPACE_ID) return;
    Promise.all([
      getCreatorInfo(WORKSPACE_ID, token).catch(() => null),
      listPublishJobs(WORKSPACE_ID, token).catch(() => null),
    ])
      .then(([info, jobsData]) => {
        setCreatorInfo(info);
        setJobs(jobsData);
      })
      .finally(() => setLoading(false));
  }, []);

  async function handlePublish() {
    if (!token || !WORKSPACE_ID || !videoUrl) return;
    setPublishing(true);
    try {
      await publishVideo(WORKSPACE_ID, { video_url: videoUrl, title: title || undefined, privacy_level: privacyLevel }, token);
      toast.success("Video published successfully");
      setVideoUrl("");
      setTitle("");
      const jobsData = await listPublishJobs(WORKSPACE_ID, token);
      setJobs(jobsData);
    } catch {
      toast.error("Failed to publish video");
    } finally {
      setPublishing(false);
    }
  }

  const publishedCount = jobs?.items.filter((j) => j.status === "PUBLISHED").length ?? 0;
  const pendingCount = jobs?.items.filter((j) => j.status === "PENDING" || j.status === "PROCESSING").length ?? 0;

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Published"
            value={publishedCount}
            icon={CheckCircle}
            iconColor="text-success"
            loading={loading}
          />
          <MetricCard
            label="In Progress"
            value={pendingCount}
            icon={Clock}
            iconColor="text-warning"
            loading={loading}
          />
          <MetricCard
            label="Total Jobs"
            value={jobs?.total ?? 0}
            icon={Upload}
            iconColor="text-coral"
            loading={loading}
          />
        </MetricBar>
      }
    >
      {/* "Open in Creative Hub" link */}
      <div className="mb-4">
        <Link
          href="/creatives/generate"
          className="inline-flex items-center gap-1 text-sm font-medium text-coral hover:text-coral-dark transition-colors"
        >
          Open in Creative Hub <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      {/* Publish form */}
      <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-[var(--shadow-card)] mb-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Publish New Video</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Video URL</label>
            <input
              type="url"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="https://example.com/video.mp4"
              className="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Title (optional)</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Video title"
              className="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Privacy</label>
            <select
              value={privacyLevel}
              onChange={(e) => setPrivacyLevel(e.target.value)}
              className="h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral appearance-none cursor-pointer"
            >
              {(creatorInfo?.privacy_level_options.length
                ? creatorInfo.privacy_level_options
                : ["PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "SELF_ONLY"]
              ).map((opt) => (
                <option key={opt} value={opt}>{opt.replace(/_/g, " ")}</option>
              ))}
            </select>
          </div>
          <button
            onClick={handlePublish}
            disabled={publishing || !videoUrl}
            className="inline-flex items-center gap-1.5 rounded-lg bg-coral px-4 py-2 text-sm font-medium text-white hover:bg-coral-dark transition-colors disabled:opacity-50"
          >
            {publishing ? "Publishing..." : "Publish Video"}
          </button>
        </div>
      </div>

      {/* Recent Publish Jobs */}
      <DataTable
        columns={columns}
        data={jobs?.items ?? []}
        keyExtractor={(row) => row.id}
        emptyTitle="No publish jobs yet"
        emptyDescription="Publish a video above to get started."
        loading={loading}
      />
    </PageShell>
  );
}
