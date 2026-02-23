"use client";

import { useEffect, useState } from "react";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
import { BarChart3, TrendingUp, FileText, AlertTriangle } from "lucide-react";

import {
  getSyncReport,
  listAdAccounts,
  type AdAccount,
  type ReportResponse,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { ChartCard } from "@/components/ui/chart-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const DATA_LEVELS = [
  { value: "AUCTION_CAMPAIGN", label: "Campaign" },
  { value: "AUCTION_ADGROUP", label: "Ad Group" },
  { value: "AUCTION_AD", label: "Ad" },
];

const AVAILABLE_METRICS = [
  "spend",
  "impressions",
  "clicks",
  "ctr",
  "cpc",
  "cpm",
  "conversions",
  "cost_per_conversion",
  "reach",
  "frequency",
  "video_views_p25",
  "video_views_p50",
  "video_views_p75",
  "video_views_p100",
];

function getDefaultDateRange(): { start: string; end: string } {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 7);
  return {
    start: start.toISOString().split("T")[0],
    end: end.toISOString().split("T")[0],
  };
}

interface ReportRow {
  dimensions: Record<string, string>;
  metrics: Record<string, string | number>;
}

export default function ReportsPage() {
  const { platform } = usePlatformFilter();
  const platformParam = platform === "all" ? undefined : platform;
  const defaultDates = getDefaultDateRange();
  const [adAccounts, setAdAccounts] = useState<AdAccount[]>([]);
  const [selectedAccount, setSelectedAccount] = useState("");
  const [dataLevel, setDataLevel] = useState("AUCTION_CAMPAIGN");
  const [dateStart, setDateStart] = useState(defaultDates.start);
  const [dateEnd, setDateEnd] = useState(defaultDates.end);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([
    "spend",
    "impressions",
    "clicks",
    "ctr",
    "conversions",
  ]);
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    listAdAccounts(WORKSPACE_ID, token).then((accounts) => {
      setAdAccounts(accounts);
      if (accounts.length > 0) setSelectedAccount(accounts[0].advertiser_id);
    }).catch(console.error);
  }, []);

  function toggleMetric(metric: string) {
    setSelectedMetrics((prev) =>
      prev.includes(metric)
        ? prev.filter((m) => m !== metric)
        : [...prev, metric]
    );
  }

  async function runReport() {
    if (!token || !selectedAccount) return;
    setLoading(true);
    try {
      const data = await getSyncReport(
        {
          ad_account_id: selectedAccount,
          data_level: dataLevel,
          date_start: dateStart,
          date_end: dateEnd,
          metrics: selectedMetrics,
          dimensions: ["stat_time_day"],
        },
        token
      );
      setReport(data);
      toast.success(`Report loaded: ${data.total_rows} rows`);
    } catch {
      toast.error("Failed to run report");
    } finally {
      setLoading(false);
    }
  }

  const metricKeys = report?.rows.length
    ? Object.keys(report.rows[0].metrics)
    : [];

  const reportColumns: Column<ReportRow>[] = [
    {
      key: "date",
      header: "Date",
      sortable: true,
      render: (row) => (
        <span className="text-sm font-medium text-gray-900">
          {row.dimensions.stat_time_day || Object.values(row.dimensions)[0] || "-"}
        </span>
      ),
    },
    ...metricKeys.map((key) => ({
      key,
      header: key.toUpperCase().replace(/_/g, " "),
      sortable: true,
      render: (row: ReportRow) => (
        <span className="text-sm text-gray-600 tabular-nums">{row.metrics[key] ?? "-"}</span>
      ),
    })),
  ];

  return (
    <>
      <PageHeader title="Ad Reports" description="Build and analyze custom performance reports" />
      <PageShell
        header={
          <MetricBar>
            <MetricCard
              label="Reports Run"
              value={report ? 1 : 0}
              icon={BarChart3}
              iconColor="text-coral"
            />
            <MetricCard
              label="Data Points"
              value={report?.total_rows ?? 0}
              icon={FileText}
              iconColor="text-info"
            />
            <MetricCard
              label="Metrics Selected"
              value={selectedMetrics.length}
              icon={TrendingUp}
              iconColor="text-purple"
            />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="Report Tip"
              description="Add 'conversions' and 'cost_per_conversion' metrics for a complete performance picture."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Date Range"
              description="Longer date ranges (30+ days) provide more reliable trend data for optimization."
              variant="warning"
            />
          </InsightPanel>
        }
      >
        {/* Report Builder */}
        <ChartCard title="Report Builder" timeRanges={[]} className="mb-6">
          <div className="h-auto -mt-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Ad Account</label>
                <select
                  value={selectedAccount}
                  onChange={(e) => setSelectedAccount(e.target.value)}
                  className="w-full h-9 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
                >
                  {adAccounts.map((a) => (
                    <option key={a.id} value={a.advertiser_id}>
                      {a.advertiser_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Data Level</label>
                <select
                  value={dataLevel}
                  onChange={(e) => setDataLevel(e.target.value)}
                  className="w-full h-9 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
                >
                  {DATA_LEVELS.map((dl) => (
                    <option key={dl.value} value={dl.value}>{dl.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Start Date</label>
                <input
                  type="date"
                  value={dateStart}
                  onChange={(e) => setDateStart(e.target.value)}
                  className="w-full h-9 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">End Date</label>
                <input
                  type="date"
                  value={dateEnd}
                  onChange={(e) => setDateEnd(e.target.value)}
                  className="w-full h-9 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
                />
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-xs text-gray-500 mb-2">Metrics</label>
              <div className="flex flex-wrap gap-2">
                {AVAILABLE_METRICS.map((metric) => (
                  <button
                    key={metric}
                    onClick={() => toggleMetric(metric)}
                    className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                      selectedMetrics.includes(metric)
                        ? "bg-coral/10 border-coral/30 text-coral font-medium"
                        : "bg-white border-gray-200 text-gray-500 hover:border-gray-300"
                    }`}
                  >
                    {metric}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={runReport}
              disabled={loading || !selectedAccount}
              className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 disabled:opacity-50 transition-colors"
            >
              {loading ? "Running..." : "Run Report"}
            </button>
          </div>
        </ChartCard>

        {/* Results Table */}
        {report && (
          <DataTable
            columns={reportColumns}
            data={report.rows}
            keyExtractor={(row) => JSON.stringify(row)}
            emptyTitle="No data for selected period"
            emptyDescription="Try adjusting the date range or metrics."
          />
        )}
      </PageShell>
    </>
  );
}
