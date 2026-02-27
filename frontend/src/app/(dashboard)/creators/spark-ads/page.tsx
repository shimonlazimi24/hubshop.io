"use client";

import { useEffect, useState } from "react";
import { Zap, CheckCircle, Clock, AlertTriangle } from "lucide-react";
import { listSparkAds, requestSparkAdAuthorization, type ContentAuthorization } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { Modal } from "@/components/ui/modal";
import { useWorkspace } from "@/hooks/useWorkspace";


const STATUS_MAP: Record<string, StatusVariant> = {
  PENDING: "warning",
  APPROVED: "active",
  EXPIRED: "paused",
  REJECTED: "error",
};

export default function SparkAdsPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const [authorizations, setAuthorizations] = useState<ContentAuthorization[]>([]);
  const [loading, setLoading] = useState(true);
  const [showRequest, setShowRequest] = useState(false);
  const [requesting, setRequesting] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");

  const [formCreatorId, setFormCreatorId] = useState("");
  const [formVideoId, setFormVideoId] = useState("");

  const token = getAccessToken();

  useEffect(() => {
    loadAuthorizations();
  }, [statusFilter]);

  function loadAuthorizations() {
    if (!token || !WORKSPACE_ID) return;
    setLoading(true);
    listSparkAds(WORKSPACE_ID, token, {
      status_filter: statusFilter || undefined,
    })
      .then(setAuthorizations)
      .catch(() => toast.error("Failed to load authorizations"))
      .finally(() => setLoading(false));
  }

  async function handleRequest() {
    if (!token || !WORKSPACE_ID || !formCreatorId.trim() || !formVideoId.trim()) return;
    setRequesting(true);
    try {
      await requestSparkAdAuthorization(WORKSPACE_ID, {
        creator_id: formCreatorId.trim(),
        platform_video_id: formVideoId.trim(),
      }, token);
      setShowRequest(false);
      setFormCreatorId("");
      setFormVideoId("");
      toast.success("Authorization request sent");
      loadAuthorizations();
    } catch {
      toast.error("Failed to request authorization");
    } finally {
      setRequesting(false);
    }
  }

  const approvedCount = authorizations.filter((a) => a.status === "APPROVED").length;
  const pendingCount = authorizations.filter((a) => a.status === "PENDING").length;
  const expiredCount = authorizations.filter((a) => a.status === "EXPIRED").length;

  const columns: Column<ContentAuthorization>[] = [
    {
      key: "creator",
      header: "Creator",
      render: (row) => <span className="text-sm font-mono">{row.creator_id.slice(0, 12)}...</span>,
    },
    {
      key: "video",
      header: "Video ID",
      render: (row) => <span className="text-sm font-mono text-gray-600">{row.platform_video_id || "-"}</span>,
    },
    {
      key: "code",
      header: "Auth Code",
      render: (row) =>
        row.authorization_code ? (
          <span className="bg-gray-50 px-2 py-1 rounded text-xs font-mono">{row.authorization_code}</span>
        ) : (
          <span className="text-gray-400">-</span>
        ),
    },
    {
      key: "status",
      header: "Status",
      render: (row) => <StatusBadge variant={STATUS_MAP[row.status] || "draft"} label={row.status} />,
    },
    {
      key: "expires",
      header: "Expires",
      render: (row) => (
        <span className="text-sm text-gray-500">
          {row.expires_at ? new Date(row.expires_at).toLocaleDateString() : "-"}
        </span>
      ),
    },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Total Authorizations" value={authorizations.length} icon={Zap} />
          <MetricCard label="Approved" value={approvedCount} icon={CheckCircle} trend={{ value: approvedCount, direction: approvedCount > 0 ? "up" : "flat" }} />
          <MetricCard label="Pending" value={pendingCount} icon={Clock} />
          <MetricCard label="Expired" value={expiredCount} icon={AlertTriangle} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Spark Ads boost" description="Spark Ads get 142% more engagement than standard in-feed ads on average." variant="success" />
          <InsightItem title="Expiring soon" description={`${expiredCount} authorization${expiredCount !== 1 ? "s" : ""} expired. Request renewals to maintain ad performance.`} variant={expiredCount > 0 ? "warning" : "default"} />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search by creator or video..."
        actions={
          <button onClick={() => setShowRequest(true)} className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 transition-colors">
            Request Authorization
          </button>
        }
      >
        <FilterDropdown
          label="Status"
          value={statusFilter}
          onChange={setStatusFilter}
          options={[
            { label: "Pending", value: "PENDING" },
            { label: "Approved", value: "APPROVED" },
            { label: "Expired", value: "EXPIRED" },
          ]}
        />
      </FilterBar>

      <DataTable
        columns={columns}
        data={authorizations}
        keyExtractor={(row) => row.id}
        loading={loading}
        emptyTitle="No Spark Ad authorizations"
        emptyDescription="Request authorization from creators to use their content as Spark Ads"
        emptyAction={{ label: "Request Authorization", onClick: () => setShowRequest(true) }}
      />

      <Modal open={showRequest} onClose={() => setShowRequest(false)} title="Request Spark Ad Authorization">
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Creator ID *</label>
            <input type="text" value={formCreatorId} onChange={(e) => setFormCreatorId(e.target.value)} placeholder="Creator ID" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">TikTok Video ID *</label>
            <input type="text" value={formVideoId} onChange={(e) => setFormVideoId(e.target.value)} placeholder="TikTok Video ID" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button onClick={() => setShowRequest(false)} className="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50">Cancel</button>
            <button onClick={handleRequest} disabled={requesting || !formCreatorId.trim() || !formVideoId.trim()} className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 disabled:opacity-50">{requesting ? "Requesting..." : "Submit Request"}</button>
          </div>
        </div>
      </Modal>
    </PageShell>
  );
}
