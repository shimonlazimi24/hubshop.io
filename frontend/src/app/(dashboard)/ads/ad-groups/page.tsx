"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
import { Layers, DollarSign, Target, TrendingUp, RefreshCw, Trophy, AlertTriangle, BarChart3 } from "lucide-react";

import {
  listAdAccounts,
  listAdGroups,
  syncAdGroups,
  type AdAccount,
  type AdGroupSummary,
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
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

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

export default function AdGroupsPage() {
  const [adGroups, setAdGroups] = useState<PaginatedResponse<AdGroupSummary> | null>(null);
  const [adAccounts, setAdAccounts] = useState<AdAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [accountFilter, setAccountFilter] = useState("");
  const [page, setPage] = useState(1);

  const { platform } = usePlatformFilter();
  const platformParam = platform === "all" ? undefined : platform;
  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    listAdAccounts(WORKSPACE_ID, token).then(setAdAccounts).catch(console.error);
  }, []);

  useEffect(() => {
    loadAdGroups();
  }, [statusFilter, accountFilter, platform, page]);

  function loadAdGroups() {
    if (!token) return;
    setLoading(true);
    listAdGroups(WORKSPACE_ID, token, {
      platform: platformParam,
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
      toast.success(`Synced ${result.synced} ad groups`);
      loadAdGroups();
    } catch {
      toast.error("Failed to sync ad groups");
    } finally {
      setSyncing(false);
    }
  }

  const columns: Column<AdGroupSummary>[] = [
    {
      key: "name",
      header: "Ad Group",
      sortable: true,
      render: (row) => (
        <Link href={`/ads/ad-groups/${row.id}`} className="text-sm font-medium text-gray-900 hover:text-coral transition-colors">
          {row.adgroup_name}
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
      key: "bid",
      header: "Bid",
      sortable: true,
      render: (row) => (
        <div>
          <span className="text-sm font-medium text-gray-900">{row.bid_amount ? `$${row.bid_amount}` : "-"}</span>
          {row.bid_type && <span className="text-xs text-gray-400 ml-1">({row.bid_type})</span>}
        </div>
      ),
    },
    {
      key: "budget",
      header: "Budget",
      sortable: true,
      render: (row) => (
        <span className="text-sm text-gray-900">{row.budget ? `$${row.budget}` : "-"}</span>
      ),
    },
    {
      key: "goal",
      header: "Optimization Goal",
      render: (row) => (
        <span className="text-sm text-gray-600">{row.optimization_goal?.replace(/_/g, " ") || "-"}</span>
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
  ];

  return (
    <>
      <PageHeader title="Ad Groups" description="Manage targeting, bidding, and budgets at the ad group level" />
      <PageShell
        header={
          <MetricBar>
            <MetricCard
              label="Total Ad Groups"
              value={adGroups?.total ?? 0}
              icon={Layers}
              iconColor="text-coral"
              trend={{ value: 3.2, direction: "up", label: "vs last week" }}
            />
            <MetricCard
              label="Avg. Bid"
              value="$2.45"
              icon={DollarSign}
              iconColor="text-success"
              trend={{ value: 5.8, direction: "down", label: "vs last week" }}
            />
            <MetricCard
              label="Avg. CTR"
              value="2.8%"
              icon={Target}
              iconColor="text-info"
              trend={{ value: 1.2, direction: "up", label: "vs last week" }}
            />
            <MetricCard
              label="Conversions"
              value="1,842"
              icon={TrendingUp}
              iconColor="text-purple"
              trend={{ value: 14.5, direction: "up", label: "vs last week" }}
              sparklineData={[120, 135, 142, 155, 168, 180, 195]}
            />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<Trophy className="h-4 w-4 text-success" />}
              title="Best Performing"
              description="'Interest-based 18-24' ad group has the lowest CPA at $2.10."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Bid Optimization"
              description="3 ad groups have bids 40% above the suggested range."
              variant="warning"
              action={{ label: "Review bids", onClick: () => {} }}
            />
            <InsightItem
              icon={<BarChart3 className="h-4 w-4 text-info" />}
              title="Audience Overlap"
              description="2 ad groups share 65% audience overlap, which may increase costs."
              variant="default"
            />
          </InsightPanel>
        }
      >
        <FilterBar
          searchValue={search}
          onSearchChange={(v) => { setSearch(v); setPage(1); }}
          searchPlaceholder="Search ad groups..."
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
          data={adGroups?.items ?? []}
          keyExtractor={(row) => row.id}
          onRowClick={(row) => { window.location.href = `/ads/ad-groups/${row.id}`; }}
          loading={loading}
          emptyTitle="No ad groups found"
          emptyDescription="Sync your TikTok ad groups or adjust your filters."
          page={adGroups?.page}
          totalPages={adGroups?.total_pages}
          onPageChange={setPage}
        />
      </PageShell>
    </>
  );
}
