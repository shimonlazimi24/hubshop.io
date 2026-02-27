"use client";

import { useEffect, useState } from "react";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
import { Package, ShoppingBag, RefreshCw, TrendingUp, AlertTriangle } from "lucide-react";
import { listCatalogs, syncCatalogs, type Catalog, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";
import { useWorkspace } from "@/hooks/useWorkspace";


export default function CatalogsPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const [data, setData] = useState<PaginatedResponse<Catalog> | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const { platform } = usePlatformFilter();
  const platformParam = platform === "all" ? undefined : platform;
  const token = getAccessToken();

  useEffect(() => {
    loadCatalogs();
  }, [platform, page]);

  function loadCatalogs() {
    if (!token || !WORKSPACE_ID) return;
    setLoading(true);
    listCatalogs(WORKSPACE_ID, token, { platform: platformParam, page })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleSync() {
    if (!token || !WORKSPACE_ID) return;
    setSyncing(true);
    try {
      await syncCatalogs(WORKSPACE_ID, token);
      toast.success("Catalogs synced successfully");
      loadCatalogs();
    } catch {
      toast.error("Failed to sync catalogs");
    } finally {
      setSyncing(false);
    }
  }

  const columns: Column<Catalog>[] = [
    {
      key: "name",
      header: "Name",
      sortable: true,
      render: (row) => <span className="text-sm font-medium text-gray-900">{row.name}</span>,
    },
    {
      key: "catalog_id",
      header: "Catalog ID",
      render: (row) => <code className="text-xs font-mono text-gray-600 bg-gray-50 px-1.5 py-0.5 rounded">{row.platform_catalog_id}</code>,
    },
    {
      key: "products",
      header: "Products",
      sortable: true,
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.product_count.toLocaleString()}</span>,
    },
    {
      key: "status",
      header: "Status",
      render: (row) => <StatusBadge variant={row.status === "ACTIVE" ? "active" : "paused"} label={row.status} />,
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
      <PageHeader title="Product Catalogs" description="Manage product feeds for dynamic product ads" />
      <PageShell
        header={
          <MetricBar>
            <MetricCard label="Total Catalogs" value={data?.total ?? 0} icon={Package} iconColor="text-coral" />
            <MetricCard label="Total Products" value="4,582" icon={ShoppingBag} iconColor="text-purple" trend={{ value: 120, direction: "up", label: "this week" }} />
            <MetricCard label="Active Catalogs" value={3} icon={Package} iconColor="text-success" />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="Feed Health"
              description="All product feeds are up to date with 99.8% match rate."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Missing Images"
              description="12 products are missing images, which may affect ad performance."
              variant="warning"
              action={{ label: "Review products", onClick: () => {} }}
            />
          </InsightPanel>
        }
      >
        <FilterBar
          searchValue={search}
          onSearchChange={(v) => { setSearch(v); setPage(1); }}
          searchPlaceholder="Search catalogs..."
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
        />

        <DataTable
          columns={columns}
          data={data?.items ?? []}
          keyExtractor={(row) => row.id}
          loading={loading}
          emptyTitle="No catalogs found"
          emptyDescription="Sync your TikTok product catalogs to get started."
          page={data?.page}
          totalPages={data?.total_pages}
          onPageChange={setPage}
        />
      </PageShell>
    </>
  );
}
