"use client";

import { useEffect, useState } from "react";
import { getRevenueVsSpend, getTopPerformers } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

export default function CommerceAnalyticsPage() {
  const [revenueData, setRevenueData] = useState<{ date: string; revenue: string; spend: string }[]>([]);
  const [topProducts, setTopProducts] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    Promise.all([
      getRevenueVsSpend(WORKSPACE_ID, token, days),
      getTopPerformers(WORKSPACE_ID, token, 10),
    ])
      .then(([revenue, performers]) => {
        setRevenueData(revenue);
        setTopProducts(performers.top_products);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [days]);

  const totalRevenue = revenueData.reduce((sum, d) => sum + parseFloat(d.revenue || "0"), 0);
  const totalSpend = revenueData.reduce((sum, d) => sum + parseFloat(d.spend || "0"), 0);

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
          <p className="text-xs text-gray-500 uppercase">Total Revenue</p>
          <p className="text-2xl font-semibold text-gray-900 mt-1">${totalRevenue.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase">Total Ad Spend</p>
          <p className="text-2xl font-semibold text-gray-900 mt-1">${totalSpend.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase">ROAS</p>
          <p className="text-2xl font-semibold text-gray-900 mt-1">
            {totalSpend > 0 ? (totalRevenue / totalSpend).toFixed(2) : "-"}x
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 mb-6">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Revenue vs Spend</h3>
        </div>
        <div className="p-4">
          {revenueData.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {revenueData.map((d) => (
                <div key={d.date} className="flex items-center gap-4 text-sm">
                  <span className="text-gray-500 w-24">{new Date(d.date).toLocaleDateString()}</span>
                  <div className="flex-1 flex items-center gap-2">
                    <div className="h-4 bg-green-400 rounded" style={{ width: `${Math.min(100, (parseFloat(d.revenue || "0") / Math.max(totalRevenue, 1)) * 100)}%` }} />
                    <span className="text-gray-700">${parseFloat(d.revenue || "0").toFixed(2)}</span>
                  </div>
                  <div className="flex-1 flex items-center gap-2">
                    <div className="h-4 bg-blue-400 rounded" style={{ width: `${Math.min(100, (parseFloat(d.spend || "0") / Math.max(totalSpend, 1)) * 100)}%` }} />
                    <span className="text-gray-700">${parseFloat(d.spend || "0").toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">No data for this period</p>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Top Products</h3>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Product</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Revenue</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Orders</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {topProducts.map((p, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{(p.name as string) || `Product ${i + 1}`}</td>
                <td className="px-4 py-3 text-sm text-gray-600">${p.revenue as string || "0"}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{(p.orders as number) || 0}</td>
              </tr>
            ))}
            {topProducts.length === 0 && (
              <tr><td colSpan={3} className="px-4 py-8 text-center text-gray-500">No product data</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Loading commerce analytics...</div>}
    </div>
  );
}
