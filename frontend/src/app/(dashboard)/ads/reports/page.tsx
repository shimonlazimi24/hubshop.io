"use client";

import { useEffect, useState } from "react";

import {
  getSyncReport,
  listAdAccounts,
  type AdAccount,
  type ReportResponse,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

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

export default function ReportsPage() {
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
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const metricKeys = report?.rows.length
    ? Object.keys(report.rows[0].metrics)
    : [];

  return (
    <div>
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Report Builder</h3>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Ad Account</label>
            <select
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">End Date</label>
            <input
              type="date"
              value={dateEnd}
              onChange={(e) => setDateEnd(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
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
                    ? "bg-blue-50 border-blue-300 text-blue-700"
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
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Running..." : "Run Report"}
        </button>
      </div>

      {report && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-4 py-3 border-b border-gray-200">
            <p className="text-sm text-gray-500">{report.total_rows} rows</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 text-left">
                  <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Date</th>
                  {metricKeys.map((key) => (
                    <th key={key} className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {report.rows.map((row, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {row.dimensions.stat_time_day || Object.values(row.dimensions)[0] || "-"}
                    </td>
                    {metricKeys.map((key) => (
                      <td key={key} className="px-4 py-3 text-sm text-gray-600">
                        {row.metrics[key] ?? "-"}
                      </td>
                    ))}
                  </tr>
                ))}
                {report.rows.length === 0 && (
                  <tr>
                    <td
                      colSpan={metricKeys.length + 1}
                      className="px-4 py-8 text-center text-gray-500"
                    >
                      No data for selected period
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
