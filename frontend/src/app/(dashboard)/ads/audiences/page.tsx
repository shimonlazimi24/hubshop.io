"use client";

import { useEffect, useState } from "react";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
import { Users, UserPlus, RefreshCw, Target, TrendingUp, AlertTriangle } from "lucide-react";
import { listAudiences, syncAudiences, type Audience, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";
import { useWorkspace } from "@/hooks/useWorkspace";


export default function AudiencesPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const [data, setData] = useState<PaginatedResponse<Audience> | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [page, setPage] = useState(1);

  const { platform } = usePlatformFilter();
  const platformParam = platform === "all" ? undefined : platform;
  const token = getAccessToken();

  useEffect(() => {
    loadAudiences();
  }, [platform, page]);

  function loadAudiences() {
    if (!token || !WORKSPACE_ID) return;
    setLoading(true);
    listAudiences(WORKSPACE_ID, token, { platform: platformParam, page })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleSync() {
    if (!token || !WORKSPACE_ID) return;
    setSyncing(true);
    try {
      await syncAudiences(WORKSPACE_ID, token);
      toast.success("Audiences synced successfully");
      loadAudiences();
    } catch {
      toast.error("Failed to sync audiences");
    } finally {
      setSyncing(false);
    }
  }

  const columns: Column<Audience>[] = [
    {
      key: "name",
      header: "Name",
      sortable: true,
      render: (row) => <span className="text-sm font-medium text-gray-900">{row.name}</span>,
    },
    {
      key: "type",
      header: "Type",
      render: (row) => (
        <StatusBadge
          variant={row.audience_type === "CUSTOM" ? "active" : "syncing"}
          label={row.audience_type}
        />
      ),
    },
    {
      key: "size",
      header: "Size",
      sortable: true,
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.size?.toLocaleString() || "-"}</span>,
    },
    {
      key: "status",
      header: "Status",
      render: (row) => <span className="text-sm text-gray-600">{row.status}</span>,
    },
    {
      key: "updated",
      header: "Updated",
      sortable: true,
      render: (row) => <span className="text-sm text-gray-500">{new Date(row.updated_at).toLocaleDateString()}</span>,
    },
  ];

  return (
    <>
      <PageHeader title="Audiences" description="Manage custom and lookalike audiences for targeting" />
      <PageShell
        header={
          <MetricBar>
            <MetricCard
              label="Total Audiences"
              value={data?.total ?? 0}
              icon={Users}
              iconColor="text-coral"
              trend={{ value: 8, direction: "up", label: "this month" }}
            />
            <MetricCard
              label="Custom Audiences"
              value={14}
              icon={UserPlus}
              iconColor="text-purple"
            />
            <MetricCard
              label="Lookalike Audiences"
              value={6}
              icon={Target}
              iconColor="text-info"
            />
            <MetricCard
              label="Avg. Match Rate"
              value="72%"
              icon={TrendingUp}
              iconColor="text-success"
              trend={{ value: 3.5, direction: "up", label: "vs last month" }}
            />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="High-Value Segment"
              description="Your 'Purchase 30d' audience has the highest conversion rate at 8.2%."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Audience Refresh"
              description="3 custom audiences haven't been refreshed in 14+ days. Performance may decline."
              variant="warning"
              action={{ label: "Refresh audiences", onClick: () => {} }}
            />
          </InsightPanel>
        }
      >
        <FilterBar
          searchValue={search}
          onSearchChange={(v) => { setSearch(v); setPage(1); }}
          searchPlaceholder="Search audiences..."
          actions={
            <button
              onClick={handleSync}
              disabled={syncing}
              className="inline-flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 disabled:opacity-50 transition-colors"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${syncing ? "animate-spin" : ""}`} />
              {syncing ? "Syncing..." : "Sync"}
            </button>
          }
        >
          <FilterDropdown
            label="All Types"
            value={typeFilter}
            options={[
              { label: "Custom", value: "CUSTOM" },
              { label: "Lookalike", value: "LOOKALIKE" },
            ]}
            onChange={(v) => { setTypeFilter(v); setPage(1); }}
          />
        </FilterBar>

        <DataTable
          columns={columns}
          data={data?.items ?? []}
          keyExtractor={(row) => row.id}
          loading={loading}
          emptyTitle="No audiences found"
          emptyDescription="Sync your TikTok audiences to get started."
          page={data?.page}
          totalPages={data?.total_pages}
          onPageChange={setPage}
        />
      </PageShell>
    </>
  );
}
