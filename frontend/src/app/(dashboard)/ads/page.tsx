"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
import { DollarSign, TrendingUp, Megaphone, Target, RefreshCw, Edit, Pause, Play, Copy, Trophy, AlertTriangle, BarChart3, Plus } from "lucide-react";

import {
  listAdAccounts,
  listCampaigns,
  syncCampaigns,
  type AdAccount,
  type CampaignSummary,
  type PaginatedResponse,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { ActionMenu } from "@/components/ui/action-menu";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const OBJECTIVES = [
  "TRAFFIC",
  "CONVERSIONS",
  "APP_INSTALL",
  "REACH",
  "VIDEO_VIEWS",
  "LEAD_GENERATION",
  "PRODUCT_SALES",
];

function mapStatus(status: string): StatusVariant {
  switch (status) {
    case "ENABLE": return "active";
    case "DISABLE": return "paused";
    case "DELETE": return "error";
    default: return "draft";
  }
}

function mapStatusLabel(status: string): string {
  switch (status) {
    case "ENABLE": return "Active";
    case "DISABLE": return "Paused";
    case "DELETE": return "Deleted";
    default: return status;
  }
}

export default function CampaignsPage() {
  const router = useRouter();
  const [campaigns, setCampaigns] = useState<PaginatedResponse<CampaignSummary> | null>(null);
  const [adAccounts, setAdAccounts] = useState<AdAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [objectiveFilter, setObjectiveFilter] = useState("");
  const [accountFilter, setAccountFilter] = useState("");
  const [page, setPage] = useState(1);
  const { platform: platformFilter } = usePlatformFilter();

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    listAdAccounts(WORKSPACE_ID, token).then(setAdAccounts).catch(console.error);
  }, []);

  useEffect(() => {
    setPage(1);
  }, [platformFilter]);

  useEffect(() => {
    loadCampaigns();
  }, [search, statusFilter, objectiveFilter, accountFilter, platformFilter, page]);

  function loadCampaigns() {
    if (!token) return;
    setLoading(true);
    const platformParam = platformFilter === "all" ? undefined : platformFilter;
    listCampaigns(WORKSPACE_ID, token, {
      search: search || undefined,
      status_filter: statusFilter || undefined,
      objective: objectiveFilter || undefined,
      ad_account_id: accountFilter || undefined,
      platform: platformParam,
      page,
    })
      .then(setCampaigns)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleSync() {
    if (!token) return;
    setSyncing(true);
    try {
      const result = await syncCampaigns(WORKSPACE_ID, token, accountFilter || undefined);
      toast.success(`Synced ${result.synced} campaigns`);
      loadCampaigns();
    } catch {
      toast.error("Failed to sync campaigns");
    } finally {
      setSyncing(false);
    }
  }

  const columns: Column<CampaignSummary>[] = [
    {
      key: "campaign_name",
      header: "Campaign",
      sortable: true,
      render: (row) => (
        <Link href={`/ads/campaigns/${row.id}`} className="text-sm font-medium text-gray-900 hover:text-coral transition-colors">
          {row.campaign_name}
        </Link>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (row) => (
        <StatusBadge variant={mapStatus(row.operation_status)} label={mapStatusLabel(row.operation_status)} />
      ),
    },
    {
      key: "platform",
      header: "Platform",
      render: (row) => (
        <StatusBadge
          variant={row.source_platform === "shop" ? "warning" : "active"}
          label={row.source_platform === "shop" ? "Shop" : "TikTok Ads"}
        />
      ),
    },
    {
      key: "objective",
      header: "Objective",
      sortable: true,
      render: (row) => (
        <span className="text-sm text-gray-600">{row.objective_type?.replace(/_/g, " ") || "-"}</span>
      ),
    },
    {
      key: "budget",
      header: "Budget",
      sortable: true,
      render: (row) => (
        <div>
          <span className="text-sm font-medium text-gray-900">{row.budget ? `$${row.budget}` : "-"}</span>
          {row.budget_mode && (
            <span className="text-xs text-gray-400 ml-1">
              ({row.budget_mode === "BUDGET_MODE_DAY" ? "daily" : row.budget_mode === "BUDGET_MODE_TOTAL" ? "total" : "infinite"})
            </span>
          )}
        </div>
      ),
    },
    {
      key: "updated",
      header: "Updated",
      sortable: true,
      render: (row) => (
        <span className="text-sm text-gray-500">{new Date(row.updated_at).toLocaleDateString()}</span>
      ),
    },
    ...(platformFilter !== "all" ? [{
      key: "actions" as const,
      header: "",
      className: "w-12",
      render: (row: CampaignSummary) => (
        <ActionMenu
          items={[
            { label: "Edit", icon: <Edit className="h-4 w-4" />, onClick: () => { window.location.href = `/ads/campaigns/${row.id}`; } },
            { label: row.operation_status === "ENABLE" ? "Pause" : "Enable", icon: row.operation_status === "ENABLE" ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />, onClick: () => toast.info("Status toggle coming soon") },
            { label: "Duplicate", icon: <Copy className="h-4 w-4" />, onClick: () => toast.info("Duplicate coming soon") },
          ]}
        />
      ),
    }] : []),
  ];

  return (
    <>
      <PageHeader
        title="Campaigns"
        description="Manage and optimize your TikTok ad campaigns"
        actions={
          <Link
            href="/ads/campaigns/new"
            className="inline-flex items-center gap-1.5 rounded-lg bg-coral px-4 py-2.5 text-sm font-medium text-white hover:bg-coral-dark transition-colors shadow-[var(--shadow-card)]"
          >
            <Plus className="h-4 w-4" />
            Create Campaign
          </Link>
        }
      />
      <PageShell
        header={
          <MetricBar>
            <MetricCard
              label="Total Spend"
              value="$12.4K"
              icon={DollarSign}
              iconColor="text-coral"
              trend={{ value: 8.2, direction: "up", label: "vs last week" }}
              sparklineData={[4200, 4800, 5100, 4900, 5600, 6200, 6800]}
            />
            <MetricCard
              label="ROAS"
              value="3.2x"
              icon={TrendingUp}
              iconColor="text-success"
              trend={{ value: 5.1, direction: "up", label: "vs last week" }}
              sparklineData={[2.8, 2.9, 3.0, 3.1, 3.0, 3.2, 3.2]}
            />
            <MetricCard
              label="Active Campaigns"
              value={12}
              icon={Megaphone}
              iconColor="text-info"
              trend={{ value: 0, direction: "flat" }}
            />
            <MetricCard
              label="CPA"
              value="$4.82"
              icon={Target}
              iconColor="text-purple"
              trend={{ value: 12.3, direction: "down", label: "vs last week" }}
              sparklineData={[6.2, 5.8, 5.5, 5.1, 5.0, 4.9, 4.8]}
            />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<Trophy className="h-4 w-4 text-success" />}
              title="Top Performer"
              description="'Spring Collection' campaign is delivering 4.8x ROAS, 50% above average."
              variant="success"
              action={{ label: "View campaign", onClick: () => {} }}
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Budget Pacing Alert"
              description="2 campaigns are on track to exhaust their daily budget by 2 PM."
              variant="warning"
              action={{ label: "Adjust budgets", onClick: () => {} }}
            />
            <InsightItem
              icon={<BarChart3 className="h-4 w-4 text-danger" />}
              title="Underperforming"
              description="'Retargeting Q1' has CPA 3x above target. Consider pausing or refreshing creatives."
              variant="danger"
              action={{ label: "Review campaign", onClick: () => {} }}
            />
          </InsightPanel>
        }
      >
        <FilterBar
          searchValue={search}
          onSearchChange={(v) => { setSearch(v); setPage(1); }}
          searchPlaceholder="Search campaigns..."
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
            label="All Statuses"
            value={statusFilter}
            options={[
              { label: "Active", value: "ENABLE" },
              { label: "Paused", value: "DISABLE" },
            ]}
            onChange={(v) => { setStatusFilter(v); setPage(1); }}
          />
          <FilterDropdown
            label="All Objectives"
            value={objectiveFilter}
            options={OBJECTIVES.map((o) => ({ label: o.replace(/_/g, " "), value: o }))}
            onChange={(v) => { setObjectiveFilter(v); setPage(1); }}
          />
          {adAccounts.length > 1 && (
            <FilterDropdown
              label="All Accounts"
              value={accountFilter}
              options={adAccounts.map((a) => ({ label: a.advertiser_name, value: a.id }))}
              onChange={(v) => { setAccountFilter(v); setPage(1); }}
            />
          )}
        </FilterBar>

        <DataTable
          columns={columns}
          data={campaigns?.items ?? []}
          keyExtractor={(row) => row.id}
          onRowClick={(row) => { window.location.href = `/ads/campaigns/${row.id}`; }}
          loading={loading}
          emptyTitle="No campaigns found"
          emptyDescription="Create your first campaign or sync existing ones from TikTok."
          emptyAction={{ label: "Create Campaign", onClick: () => router.push("/ads/campaigns/new") }}
          page={campaigns?.page}
          totalPages={campaigns?.total_pages}
          onPageChange={setPage}
        />
      </PageShell>
    </>
  );
}
