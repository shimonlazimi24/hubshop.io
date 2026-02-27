"use client";

import { useEffect, useState } from "react";
import { DollarSign, TrendingUp, ShoppingCart, Megaphone } from "lucide-react";
import { getAnalyticsOverview, getTopPerformers, getRevenueVsSpend } from "@/lib/api";
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


interface SpendRow {
  date: string;
  revenue: string;
  spend: string;
}

interface CampaignRow {
  name: string;
  spend: string;
  impressions: number;
  conversions: number;
}

export default function AdvertisingAnalyticsPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const [overview, setOverview] = useState<{
    total_ad_spend: string;
    roas: string;
    total_orders: number;
  } | null>(null);
  const [spendData, setSpendData] = useState<SpendRow[]>([]);
  const [topCampaigns, setTopCampaigns] = useState<CampaignRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState("30");

  const token = getAccessToken();

  useEffect(() => {
    if (!token || !WORKSPACE_ID) return;
    setLoading(true);
    Promise.all([
      getAnalyticsOverview(WORKSPACE_ID, token, Number(days)),
      getRevenueVsSpend(WORKSPACE_ID, token, Number(days)),
      getTopPerformers(WORKSPACE_ID, token, 10),
    ])
      .then(([ov, spend, performers]) => {
        setOverview({ total_ad_spend: ov.total_ad_spend, roas: ov.roas, total_orders: ov.total_orders });
        setSpendData(spend);
        setTopCampaigns(
          (performers.top_campaigns || []).map((c: Record<string, unknown>) => ({
            name: (c.name as string) || "Unnamed",
            spend: (c.spend as string) || "0",
            impressions: (c.impressions as number) || 0,
            conversions: (c.conversions as number) || 0,
          }))
        );
      })
      .catch(() => toast.error("Failed to load advertising analytics"))
      .finally(() => setLoading(false));
  }, [days]);

  const totalSpend = spendData.reduce((sum, d) => sum + parseFloat(d.spend || "0"), 0);

  const campaignColumns: Column<CampaignRow>[] = [
    {
      key: "name",
      header: "Campaign",
      render: (row) => <span className="text-sm font-medium text-gray-900">{row.name}</span>,
    },
    {
      key: "spend",
      header: "Spend",
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">${row.spend}</span>,
    },
    {
      key: "impressions",
      header: "Impressions",
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.impressions.toLocaleString()}</span>,
    },
    {
      key: "conversions",
      header: "Conversions",
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.conversions}</span>,
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
            <MetricCard label="Total Ad Spend" value={`$${overview?.total_ad_spend || "0"}`} icon={DollarSign} />
            <MetricCard label="ROAS" value={`${overview?.roas || "0"}x`} icon={TrendingUp} />
            <MetricCard label="Conversions" value={overview?.total_orders.toLocaleString() || "0"} icon={ShoppingCart} />
          </MetricBar>
        )
      }
      aside={
        <InsightPanel>
          <InsightItem
            title="Ad performance"
            description={overview ? `ROAS of ${overview.roas}x with ${overview.total_orders} conversions in the selected period.` : "Loading..."}
            variant={overview && parseFloat(overview.roas) >= 2 ? "success" : "default"}
          />
          <InsightItem
            title="Spend trend"
            description={`$${totalSpend.toFixed(2)} total spend across ${spendData.length} days.`}
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

      {/* Daily Ad Spend */}
      <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] mb-6">
        <div className="px-4 py-3 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-900">Daily Ad Spend</h3>
        </div>
        <div className="p-4">
          {spendData.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {spendData.map((d) => (
                <div key={d.date} className="flex items-center gap-4 text-sm">
                  <span className="text-gray-500 w-24">{new Date(d.date).toLocaleDateString()}</span>
                  <div className="flex-1 flex items-center gap-2">
                    <div
                      className="h-4 bg-blue-400 rounded"
                      style={{ width: `${Math.min(100, (parseFloat(d.spend || "0") / Math.max(totalSpend, 1)) * 100)}%` }}
                    />
                    <span className="text-gray-700 tabular-nums">${parseFloat(d.spend || "0").toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-400 py-8">No spend data for this period</p>
          )}
        </div>
      </div>

      {/* Top Campaigns */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Megaphone className="h-4 w-4 text-purple-500" />
          <h3 className="text-sm font-semibold text-gray-900">Top Campaigns</h3>
        </div>
        <DataTable
          columns={campaignColumns}
          data={topCampaigns}
          keyExtractor={(row) => row.name}
          emptyTitle="No campaign data"
          emptyDescription="Campaign performance data will appear here"
        />
      </div>
    </PageShell>
  );
}
