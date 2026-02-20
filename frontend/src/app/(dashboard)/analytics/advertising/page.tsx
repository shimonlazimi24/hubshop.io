"use client";

import { useEffect, useState } from "react";
import { getAnalyticsOverview, getTopPerformers, getRevenueVsSpend } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

export default function AdvertisingAnalyticsPage() {
  const [overview, setOverview] = useState<{
    total_ad_spend: string;
    roas: string;
    total_orders: number;
  } | null>(null);
  const [spendData, setSpendData] = useState<{ date: string; revenue: string; spend: string }[]>([]);
  const [topCampaigns, setTopCampaigns] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    Promise.all([
      getAnalyticsOverview(WORKSPACE_ID, token, days),
      getRevenueVsSpend(WORKSPACE_ID, token, days),
      getTopPerformers(WORKSPACE_ID, token, 10),
    ])
      .then(([ov, spend, performers]) => {
        setOverview({ total_ad_spend: ov.total_ad_spend, roas: ov.roas, total_orders: ov.total_orders });
        setSpendData(spend);
        setTopCampaigns(performers.top_campaigns);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [days]);

  const totalSpend = spendData.reduce((sum, d) => sum + parseFloat(d.spend || "0"), 0);

  return (
    <div>
      <div className="flex items-center gap-4 mb-4">
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase">Total Ad Spend</p>
          <p className="text-2xl font-semibold text-gray-900 mt-1">${overview?.total_ad_spend || "0"}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase">ROAS</p>
          <p className="text-2xl font-semibold text-gray-900 mt-1">{overview?.roas || "0"}x</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase">Conversions</p>
          <p className="text-2xl font-semibold text-gray-900 mt-1">{overview?.total_orders.toLocaleString() || "0"}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 mb-6">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Daily Ad Spend</h3>
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
                    <span className="text-gray-700">${parseFloat(d.spend || "0").toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">No spend data for this period</p>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Top Campaigns</h3>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Campaign</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Spend</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Impressions</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Conversions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {topCampaigns.map((c, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{(c.name as string) || `Campaign ${i + 1}`}</td>
                <td className="px-4 py-3 text-sm text-gray-600">${(c.spend as string) || "0"}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{((c.impressions as number) || 0).toLocaleString()}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{(c.conversions as number) || 0}</td>
              </tr>
            ))}
            {topCampaigns.length === 0 && (
              <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">No campaign data</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Loading advertising analytics...</div>}
    </div>
  );
}
