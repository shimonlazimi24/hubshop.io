"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
import {
  DollarSign,
  ShoppingCart,
  TrendingUp,
  RotateCcw,
  RefreshCw,
  AlertTriangle,
  Lightbulb,
} from "lucide-react";
import {
  listOrders,
  listShops,
  syncShops,
  type OrderSummary,
  type PaginatedResponse,
  type Shop,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { useCommerceWebSocket, type CommerceWSMessage } from "@/hooks/useCommerceWebSocket";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { EmptyState } from "@/components/ui/empty-state";
import { toast } from "@/lib/toast-store";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_MAP: Record<string, StatusVariant> = {
  awaiting_shipment: "warning",
  in_transit: "syncing",
  delivered: "completed",
  completed: "completed",
  cancelled: "error",
  unpaid: "draft",
};

export default function CommerceOrdersPage() {
  const [shops, setShops] = useState<Shop[]>([]);
  const [orders, setOrders] = useState<PaginatedResponse<OrderSummary> | null>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [liveUpdates, setLiveUpdates] = useState<string[]>([]);
  const { platform: platformFilter } = usePlatformFilter();

  const token = getAccessToken();

  useCommerceWebSocket({
    workspaceId: WORKSPACE_ID,
    token,
    onMessage: (msg: CommerceWSMessage) => {
      if (msg.type === "order_status_change") {
        setLiveUpdates((prev) => [String(msg.order_id), ...prev.slice(0, 9)]);
        loadOrders();
      }
    },
  });

  useEffect(() => {
    setPage(1);
  }, [platformFilter]);

  useEffect(() => {
    loadShops();
    loadOrders();
  }, [statusFilter, platformFilter, page]);

  function loadShops() {
    if (!token) return;
    listShops(WORKSPACE_ID, token).then(setShops).catch(console.error);
  }

  function loadOrders() {
    if (!token) return;
    setLoading(true);
    const platformParam = platformFilter === "all" ? undefined : platformFilter;
    listOrders(WORKSPACE_ID, token, {
      status_filter: statusFilter || undefined,
      platform: platformParam,
      page,
    })
      .then(setOrders)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleSyncShops() {
    if (!token) return;
    try {
      await syncShops(WORKSPACE_ID, token);
      toast.success("Shops synced successfully");
      loadShops();
    } catch {
      toast.error("Failed to sync shops");
    }
  }

  if (shops.length === 0 && !loading) {
    return (
      <EmptyState
        icon={ShoppingCart}
        title="No shops connected yet"
        description="Connect a TikTok Shop account first, then sync your shops."
        action={{ label: "Connect Account", onClick: () => { window.location.href = "/connect"; } }}
      />
    );
  }

  const totalRevenue = orders?.items.reduce((s, o) => s + parseFloat(o.total_amount || "0"), 0) ?? 0;
  const totalOrders = orders?.total ?? 0;
  const aov = totalOrders > 0 ? (totalRevenue / totalOrders) : 0;

  const columns: Column<OrderSummary>[] = [
    {
      key: "order_id",
      header: "Order ID",
      render: (row) => (
        <div className="flex items-center gap-2">
          <Link
            href={`/commerce/orders/${row.id}`}
            className="text-sm font-medium text-coral hover:text-coral-dark transition-colors"
          >
            {row.platform_order_id}
          </Link>
          {liveUpdates.includes(row.id) && (
            <span className="inline-block w-2 h-2 bg-info rounded-full animate-pulse" />
          )}
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
      key: "platform",
      header: "Platform",
      render: (row) => (
        <StatusBadge
          variant={row.source_platform === "affiliate" ? "syncing" : "active"}
          label={row.source_platform === "affiliate" ? "Affiliate" : "Shop"}
        />
      ),
    },
    {
      key: "total",
      header: "Total",
      sortable: true,
      render: (row) => (
        <span className="text-sm font-medium text-gray-900 tabular-nums">
          {row.currency} {row.total_amount}
        </span>
      ),
    },
    {
      key: "items",
      header: "Items",
      render: (row) => <span className="text-sm text-gray-600">{row.item_count}</span>,
    },
    {
      key: "sla",
      header: "SLA",
      render: (row) => {
        if (!row.rts_sla) return <span className="text-sm text-gray-400">-</span>;
        const slaDate = new Date(row.rts_sla);
        const isOverdue = slaDate < new Date();
        const isUrgent = slaDate.getTime() - Date.now() < 86400000;
        return (
          <span className={`text-sm font-medium ${isOverdue ? "text-danger" : isUrgent ? "text-warning" : "text-success"}`}>
            {slaDate.toLocaleDateString()}
          </span>
        );
      },
    },
    {
      key: "date",
      header: "Date",
      sortable: true,
      render: (row) => (
        <span className="text-sm text-gray-500">{new Date(row.created_at).toLocaleDateString()}</span>
      ),
    },
  ];

  return (
    <>
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Revenue"
            value={`$${totalRevenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
            icon={DollarSign}
            iconColor="text-success"
            trend={{ value: 12.5, direction: "up", label: "vs last week" }}
            sparklineData={[3200, 3500, 3800, 3600, 4000, 4200, 4500]}
            loading={loading}
          />
          <MetricCard
            label="Orders"
            value={totalOrders}
            icon={ShoppingCart}
            iconColor="text-coral"
            trend={{ value: 8.1, direction: "up", label: "vs last week" }}
            sparklineData={[42, 45, 48, 44, 50, 52, 55]}
            loading={loading}
          />
          <MetricCard
            label="AOV"
            value={`$${aov.toFixed(2)}`}
            icon={TrendingUp}
            iconColor="text-purple"
            trend={{ value: 3.2, direction: "up", label: "vs last week" }}
            loading={loading}
          />
          <MetricCard
            label="Refund Rate"
            value="2.1%"
            icon={RotateCcw}
            iconColor="text-warning"
            trend={{ value: 0.5, direction: "down", label: "vs last week" }}
            loading={loading}
          />
        </MetricBar>
      }
      aside={
        <InsightPanel defaultOpen={false}>
          <InsightItem
            icon={<AlertTriangle className="h-4 w-4 text-warning" />}
            title="SLA at risk"
            description="5 orders are approaching their ship-by deadline. Process them within 4 hours."
            variant="warning"
            action={{ label: "View orders", onClick: () => setStatusFilter("awaiting_shipment") }}
          />
          <InsightItem
            icon={<TrendingUp className="h-4 w-4 text-success" />}
            title="Revenue trending up"
            description="Revenue is up 12.5% this week. Your best-selling product contributed 30% of sales."
            variant="success"
          />
          <InsightItem
            icon={<Lightbulb className="h-4 w-4 text-coral" />}
            title="Fulfillment tip"
            description="Orders shipped within 24h have 40% higher customer satisfaction scores."
            variant="default"
          />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={(v) => setSearch(v)}
        searchPlaceholder="Search orders..."
        actions={
          <button
            onClick={handleSyncShops}
            className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Sync
          </button>
        }
      >
        <FilterDropdown
          label="All Statuses"
          value={statusFilter}
          options={[
            { label: "Awaiting Shipment", value: "awaiting_shipment" },
            { label: "In Transit", value: "in_transit" },
            { label: "Delivered", value: "delivered" },
            { label: "Completed", value: "completed" },
            { label: "Cancelled", value: "cancelled" },
          ]}
          onChange={(v) => { setStatusFilter(v); setPage(1); }}
        />
      </FilterBar>

      <DataTable
        columns={columns}
        data={orders?.items ?? []}
        keyExtractor={(row) => row.id}
        onRowClick={(row) => { window.location.href = `/commerce/orders/${row.id}`; }}
        emptyTitle="No orders found"
        emptyDescription="Orders will appear here once your shop is connected and synced."
        page={orders?.page}
        totalPages={orders?.total_pages}
        onPageChange={setPage}
        loading={loading}
      />
    </PageShell>
    </>
  );
}
