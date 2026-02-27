"use client";

import { useEffect, useState } from "react";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
import { DollarSign, ShoppingCart, TrendingUp, RotateCcw } from "lucide-react";
import {
  getCommerceSummary,
  getOrderDistribution,
  getRevenueTimeseries,
  getTopProducts,
  type OrderStatusDistribution,
  type RevenuePoint,
  type RevenueSummary,
  type TopProduct,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { ChartCard } from "@/components/ui/chart-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { useWorkspace } from "@/hooks/useWorkspace";


const topProductColumns: Column<TopProduct>[] = [
  {
    key: "product",
    header: "Product",
    render: (row) => (
      <div className="flex items-center gap-3">
        {row.main_image_url && (
          <img src={row.main_image_url} alt="" className="w-8 h-8 rounded-lg object-cover" />
        )}
        <span className="text-sm text-gray-900">{row.title}</span>
      </div>
    ),
  },
  {
    key: "revenue",
    header: "Revenue",
    sortable: true,
    render: (row) => <span className="text-sm font-medium text-gray-900 tabular-nums">${row.total_revenue}</span>,
  },
  {
    key: "quantity",
    header: "Quantity",
    sortable: true,
    render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.total_quantity}</span>,
  },
];

export default function AnalyticsPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const [summary, setSummary] = useState<RevenueSummary | null>(null);
  const [timeseries, setTimeseries] = useState<RevenuePoint[]>([]);
  const [topProducts, setTopProducts] = useState<TopProduct[]>([]);
  const [distribution, setDistribution] = useState<OrderStatusDistribution[]>([]);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);

  const { platform } = usePlatformFilter();
  const platformParam = platform === "all" ? undefined : platform;
  const token = getAccessToken();

  useEffect(() => {
    if (!token || !WORKSPACE_ID) return;
    setLoading(true);

    Promise.all([
      getCommerceSummary(WORKSPACE_ID, token, days, platformParam),
      getRevenueTimeseries(WORKSPACE_ID, token, days, platformParam),
      getTopProducts(WORKSPACE_ID, token, 10, platformParam),
      getOrderDistribution(WORKSPACE_ID, token, platformParam),
    ])
      .then(([s, t, p, d]) => {
        setSummary(s);
        setTimeseries(t);
        setTopProducts(p);
        setDistribution(d);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [days, platform]);

  const maxRevenue = Math.max(
    ...timeseries.map((p) => parseFloat(p.revenue) || 0),
    1
  );

  return (
    <PageShell
      header={
        summary ? (
          <MetricBar>
            <MetricCard
              label="Revenue"
              value={`$${summary.total_revenue}`}
              icon={DollarSign}
              iconColor="text-success"
              trend={{ value: 12.5, direction: "up", label: `${days}d` }}
              sparklineData={timeseries.map((p) => parseFloat(p.revenue) || 0)}
              loading={loading}
            />
            <MetricCard
              label="Orders"
              value={summary.total_orders}
              icon={ShoppingCart}
              iconColor="text-coral"
              trend={{ value: 8.1, direction: "up", label: `${days}d` }}
              sparklineData={timeseries.map((p) => p.order_count)}
              loading={loading}
            />
            <MetricCard
              label="AOV"
              value={`$${summary.average_order_value}`}
              icon={TrendingUp}
              iconColor="text-purple"
              loading={loading}
            />
            <MetricCard
              label="Return Rate"
              value={`${(summary.return_rate * 100).toFixed(1)}%`}
              icon={RotateCcw}
              iconColor="text-warning"
              loading={loading}
            />
          </MetricBar>
        ) : undefined
      }
      aside={
        <InsightPanel defaultOpen={false}>
          <InsightItem
            icon={<TrendingUp className="h-4 w-4 text-success" />}
            title="Revenue growing"
            description="Revenue has grown 12.5% over the selected period. Your top product accounts for 28% of total sales."
            variant="success"
          />
          <InsightItem
            icon={<RotateCcw className="h-4 w-4 text-warning" />}
            title="Return rate stable"
            description="Your return rate is stable at 2.1%, well below the category average."
            variant="default"
          />
        </InsightPanel>
      }
    >
      {/* Period selector */}
      <div className="flex items-center gap-1 rounded-lg bg-gray-100 p-0.5 w-fit mb-6">
        {[7, 14, 30, 90].map((d) => (
          <button
            key={d}
            onClick={() => setDays(d)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition-all duration-[var(--duration-fast)] ${
              days === d
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {d}D
          </button>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <ChartCard title="Revenue Trend" timeRanges={[]}>
          {timeseries.length > 0 ? (
            <div className="flex items-end gap-1 h-full px-2">
              {timeseries.map((point) => {
                const height = ((parseFloat(point.revenue) || 0) / maxRevenue) * 100;
                return (
                  <div key={point.date} className="flex-1 group relative">
                    <div
                      className="bg-coral/80 rounded-t hover:bg-coral transition-colors"
                      style={{ height: `${Math.max(height, 2)}%` }}
                    />
                    <div className="hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap z-10">
                      {point.date}: ${point.revenue}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-500 flex items-center justify-center h-full">No data for this period</p>
          )}
        </ChartCard>

        <ChartCard title="Order Distribution" timeRanges={[]}>
          {distribution.length > 0 ? (
            <div className="space-y-3 p-2">
              {distribution.map((d) => (
                <div key={d.status}>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-700">{d.status.replace(/_/g, " ")}</span>
                    <span className="text-gray-500 tabular-nums">{d.count} ({d.percentage}%)</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-coral h-2 rounded-full transition-all"
                      style={{ width: `${d.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500 flex items-center justify-center h-full">No order data</p>
          )}
        </ChartCard>
      </div>

      {/* Top Products */}
      <h3 className="text-sm font-semibold text-gray-900 mb-3">Top Products</h3>
      <DataTable
        columns={topProductColumns}
        data={topProducts}
        keyExtractor={(row) => row.title}
        emptyTitle="No product data yet"
        emptyDescription="Product rankings will appear once you have order data."
        loading={loading}
      />
    </PageShell>
  );
}
