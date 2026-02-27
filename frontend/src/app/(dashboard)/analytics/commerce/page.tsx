"use client";

import { useEffect, useState } from "react";
import { DollarSign, TrendingUp, ShoppingBag, Package } from "lucide-react";
import { getRevenueVsSpend, getTopPerformers } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { toast } from "@/lib/toast-store";
import { Skeleton } from "@/components/ui/skeleton";
import { useWorkspace } from "@/hooks/useWorkspace";


interface RevenueRow {
  date: string;
  revenue: string;
  spend: string;
}

interface ProductRow {
  name: string;
  revenue: string;
  orders: number;
}

export default function CommerceAnalyticsPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const [revenueData, setRevenueData] = useState<RevenueRow[]>([]);
  const [topProducts, setTopProducts] = useState<ProductRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState("30");

  const token = getAccessToken();

  useEffect(() => {
    if (!token || !WORKSPACE_ID) return;
    setLoading(true);
    Promise.all([
      getRevenueVsSpend(WORKSPACE_ID, token, Number(days)),
      getTopPerformers(WORKSPACE_ID, token, 10),
    ])
      .then(([revenue, performers]) => {
        setRevenueData(revenue);
        setTopProducts(
          (performers.top_products || []).map((p: Record<string, unknown>) => ({
            name: (p.name as string) || "Unnamed",
            revenue: (p.revenue as string) || "0",
            orders: (p.orders as number) || 0,
          }))
        );
      })
      .catch(() => toast.error("Failed to load commerce analytics"))
      .finally(() => setLoading(false));
  }, [days]);

  const totalRevenue = revenueData.reduce((sum, d) => sum + parseFloat(d.revenue || "0"), 0);
  const totalSpend = revenueData.reduce((sum, d) => sum + parseFloat(d.spend || "0"), 0);

  const productColumns: Column<ProductRow>[] = [
    {
      key: "name",
      header: "Product",
      render: (row) => <span className="text-sm font-medium text-gray-900">{row.name}</span>,
    },
    {
      key: "revenue",
      header: "Revenue",
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">${row.revenue}</span>,
    },
    {
      key: "orders",
      header: "Orders",
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.orders}</span>,
    },
  ];

  return (
    <PageShell
      header={
        loading ? (
          <MetricBar>
            <Skeleton className="h-16 flex-1 rounded-xl" />
            <Skeleton className="h-16 flex-1 rounded-xl" />
            <Skeleton className="h-16 flex-1 rounded-xl" />
          </MetricBar>
        ) : (
          <MetricBar>
            <MetricCard label="Total Revenue" value={`$${totalRevenue.toFixed(2)}`} icon={DollarSign} />
            <MetricCard label="Total Ad Spend" value={`$${totalSpend.toFixed(2)}`} icon={ShoppingBag} />
            <MetricCard
              label="ROAS"
              value={`${totalSpend > 0 ? (totalRevenue / totalSpend).toFixed(2) : "-"}x`}
              icon={TrendingUp}
              trend={totalSpend > 0 && totalRevenue / totalSpend >= 2 ? { value: totalRevenue / totalSpend, direction: "up" } : undefined}
            />
          </MetricBar>
        )
      }
      aside={
        <InsightPanel>
          <InsightItem
            title="Revenue overview"
            description={`$${totalRevenue.toFixed(2)} total revenue over ${revenueData.length} days.`}
            variant={totalRevenue > 0 ? "success" : "default"}
          />
          <InsightItem
            title="Profitability"
            description={totalSpend > 0 ? `ROAS of ${(totalRevenue / totalSpend).toFixed(2)}x. ${totalRevenue > totalSpend ? "Revenue exceeds ad spend." : "Ad spend exceeds revenue."}` : "No ad spend data."}
          />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue=""
        onSearchChange={() => {}}
        searchPlaceholder=""
      >
        <FilterDropdown
          label="Period"
          value={days}
          onChange={setDays}
          options={[
            { label: "Last 7 days", value: "7" },
            { label: "Last 30 days", value: "30" },
            { label: "Last 90 days", value: "90" },
          ]}
        />
      </FilterBar>

      {/* Revenue vs Spend Chart */}
      <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] mb-6">
        <div className="px-4 py-3 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-900">Revenue vs Spend</h3>
        </div>
        <div className="p-4">
          {revenueData.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {revenueData.map((d) => (
                <div key={d.date} className="flex items-center gap-4 text-sm">
                  <span className="text-gray-500 w-24">{new Date(d.date).toLocaleDateString()}</span>
                  <div className="flex-1 flex items-center gap-2">
                    <div className="h-4 bg-green-400 rounded" style={{ width: `${Math.min(100, (parseFloat(d.revenue || "0") / Math.max(totalRevenue, 1)) * 100)}%` }} />
                    <span className="text-gray-700 tabular-nums">${parseFloat(d.revenue || "0").toFixed(2)}</span>
                  </div>
                  <div className="flex-1 flex items-center gap-2">
                    <div className="h-4 bg-blue-400 rounded" style={{ width: `${Math.min(100, (parseFloat(d.spend || "0") / Math.max(totalSpend, 1)) * 100)}%` }} />
                    <span className="text-gray-700 tabular-nums">${parseFloat(d.spend || "0").toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-400 py-8">No data for this period</p>
          )}
        </div>
      </div>

      {/* Top Products */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Package className="h-4 w-4 text-emerald-500" />
          <h3 className="text-sm font-semibold text-gray-900">Top Products</h3>
        </div>
        <DataTable
          columns={productColumns}
          data={topProducts}
          keyExtractor={(row) => row.name}
          emptyTitle="No product data"
          emptyDescription="Product performance data will appear here"
        />
      </div>
    </PageShell>
  );
}
