"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
import { Package, RefreshCw, LayoutGrid, List, AlertTriangle, TrendingUp } from "lucide-react";
import {
  listProducts,
  listShops,
  syncProducts,
  type PaginatedResponse,
  type ProductSummary,
  type Shop,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { toast } from "@/lib/toast-store";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_MAP: Record<string, StatusVariant> = {
  live: "active",
  pending: "warning",
  draft: "draft",
  seller_deactivated: "error",
  platform_deactivated: "error",
  frozen: "paused",
  deleted: "error",
};

export default function ProductsPage() {
  const [products, setProducts] = useState<PaginatedResponse<ProductSummary> | null>(null);
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [shopFilter, setShopFilter] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"grid" | "table">("table");

  const { platform } = usePlatformFilter();
  const platformParam = platform === "all" ? undefined : platform;
  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    listShops(WORKSPACE_ID, token).then(setShops).catch(console.error);
  }, []);

  useEffect(() => {
    loadProducts();
  }, [search, statusFilter, shopFilter, platform, page]);

  function loadProducts() {
    if (!token) return;
    setLoading(true);
    listProducts(WORKSPACE_ID, token, {
      platform: platformParam,
      search: search || undefined,
      status_filter: statusFilter || undefined,
      shop_id: shopFilter || undefined,
      page,
    })
      .then(setProducts)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleSync() {
    if (!token) return;
    setSyncing(true);
    try {
      const result = await syncProducts(WORKSPACE_ID, token);
      toast.success(`Synced ${result.synced} products`);
      loadProducts();
    } catch {
      toast.error("Failed to sync products");
    } finally {
      setSyncing(false);
    }
  }

  const items = products?.items ?? [];
  const liveCount = items.filter((p) => p.status === "live").length;
  const totalInventory = items.reduce((s, p) => s + (p.inventory_total || 0), 0);

  const columns: Column<ProductSummary>[] = [
    {
      key: "product",
      header: "Product",
      render: (row) => (
        <div className="flex items-center gap-3">
          {row.main_image_url && (
            <img src={row.main_image_url} alt="" className="w-10 h-10 rounded-lg object-cover" />
          )}
          <Link
            href={`/commerce/products/${row.id}`}
            className="text-sm font-medium text-coral hover:text-coral-dark transition-colors line-clamp-1"
          >
            {row.title}
          </Link>
        </div>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (row) => (
        <StatusBadge
          variant={STATUS_MAP[row.status] || "draft"}
          label={row.status.replace(/_/g, " ")}
        />
      ),
    },
    {
      key: "price",
      header: "Price",
      sortable: true,
      render: (row) => (
        <span className="text-sm text-gray-900 tabular-nums">
          {row.price_amount ? `${row.currency || "$"} ${row.price_amount}` : "-"}
        </span>
      ),
    },
    {
      key: "inventory",
      header: "Inventory",
      sortable: true,
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.inventory_total}</span>,
    },
    {
      key: "skus",
      header: "SKUs",
      render: (row) => <span className="text-sm text-gray-600">{row.sku_count}</span>,
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
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Total Products"
            value={products?.total ?? 0}
            icon={Package}
            iconColor="text-coral"
            loading={loading}
          />
          <MetricCard
            label="Live Products"
            value={liveCount}
            icon={TrendingUp}
            iconColor="text-success"
            loading={loading}
          />
          <MetricCard
            label="Total Inventory"
            value={totalInventory.toLocaleString()}
            icon={Package}
            iconColor="text-info"
            loading={loading}
          />
        </MetricBar>
      }
      aside={
        <InsightPanel defaultOpen={false}>
          <InsightItem
            icon={<AlertTriangle className="h-4 w-4 text-warning" />}
            title="Low stock alert"
            description="3 products have inventory below 10 units. Consider restocking soon."
            variant="warning"
          />
          <InsightItem
            icon={<TrendingUp className="h-4 w-4 text-success" />}
            title="Best seller"
            description="Your top product has sold 142 units this week, a 25% increase."
            variant="success"
          />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={(v) => { setSearch(v); setPage(1); }}
        searchPlaceholder="Search products..."
        actions={
          <div className="flex items-center gap-2">
            {/* View toggle */}
            <div className="flex items-center rounded-lg border border-gray-200 p-0.5">
              <button
                onClick={() => setViewMode("grid")}
                className={`flex h-7 w-7 items-center justify-center rounded-md transition-colors ${viewMode === "grid" ? "bg-gray-100 text-gray-900" : "text-gray-400 hover:text-gray-600"}`}
              >
                <LayoutGrid className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => setViewMode("table")}
                className={`flex h-7 w-7 items-center justify-center rounded-md transition-colors ${viewMode === "table" ? "bg-gray-100 text-gray-900" : "text-gray-400 hover:text-gray-600"}`}
              >
                <List className="h-3.5 w-3.5" />
              </button>
            </div>
            <button
              onClick={handleSync}
              disabled={syncing}
              className="inline-flex items-center gap-1.5 rounded-lg bg-coral px-4 py-2 text-sm font-medium text-white hover:bg-coral-dark transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${syncing ? "animate-spin" : ""}`} />
              {syncing ? "Syncing..." : "Sync Products"}
            </button>
          </div>
        }
      >
        <FilterDropdown
          label="All Statuses"
          value={statusFilter}
          options={[
            { label: "Live", value: "live" },
            { label: "Pending", value: "pending" },
            { label: "Draft", value: "draft" },
            { label: "Deactivated", value: "seller_deactivated" },
          ]}
          onChange={(v) => { setStatusFilter(v); setPage(1); }}
        />
        {shops.length > 1 && (
          <FilterDropdown
            label="All Shops"
            value={shopFilter}
            options={shops.map((s) => ({ label: s.shop_name, value: s.id }))}
            onChange={(v) => { setShopFilter(v); setPage(1); }}
          />
        )}
      </FilterBar>

      {viewMode === "grid" ? (
        /* Grid view */
        <>
          {!loading && items.length === 0 ? (
            <div className="rounded-lg border border-gray-200 bg-white">
              <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
                <Package className="h-8 w-8 text-gray-300 mb-3" />
                <p className="text-sm font-semibold text-gray-900 mb-1">No products found</p>
                <p className="text-sm text-gray-500">Sync your products from TikTok Shop to get started.</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {items.map((product) => (
                <Link
                  key={product.id}
                  href={`/commerce/products/${product.id}`}
                  className="group rounded-xl border border-gray-100 bg-white overflow-hidden shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-panel)] transition-all duration-[var(--duration-fast)]"
                >
                  <div className="aspect-square bg-gray-100">
                    {product.main_image_url ? (
                      <img src={product.main_image_url} alt="" className="w-full h-full object-cover" />
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <Package className="h-8 w-8 text-gray-300" />
                      </div>
                    )}
                  </div>
                  <div className="p-3">
                    <h4 className="text-sm font-medium text-gray-900 truncate mb-1">{product.title}</h4>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-gray-900">
                        {product.price_amount ? `${product.currency || "$"}${product.price_amount}` : "-"}
                      </span>
                      <StatusBadge
                        variant={STATUS_MAP[product.status] || "draft"}
                        label={product.status.replace(/_/g, " ")}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{product.inventory_total} in stock</p>
                  </div>
                </Link>
              ))}
            </div>
          )}
          {/* Grid pagination */}
          {products && products.total_pages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <p className="text-xs text-gray-500">Page {products.page} of {products.total_pages}</p>
              <div className="flex gap-1">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 transition-colors"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(products.total_pages, p + 1))}
                  disabled={page >= products.total_pages}
                  className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      ) : (
        /* Table view */
        <DataTable
          columns={columns}
          data={items}
          keyExtractor={(row) => row.id}
          onRowClick={(row) => { window.location.href = `/commerce/products/${row.id}`; }}
          emptyTitle="No products found"
          emptyDescription="Sync your products from TikTok Shop to get started."
          page={products?.page}
          totalPages={products?.total_pages}
          onPageChange={setPage}
          loading={loading}
        />
      )}
    </PageShell>
  );
}
