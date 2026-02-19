"use client";

import { useEffect, useState } from "react";

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

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<RevenueSummary | null>(null);
  const [timeseries, setTimeseries] = useState<RevenuePoint[]>([]);
  const [topProducts, setTopProducts] = useState<TopProduct[]>([]);
  const [distribution, setDistribution] = useState<OrderStatusDistribution[]>([]);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    setLoading(true);

    Promise.all([
      getCommerceSummary(WORKSPACE_ID, token, days),
      getRevenueTimeseries(WORKSPACE_ID, token, days),
      getTopProducts(WORKSPACE_ID, token, 10),
      getOrderDistribution(WORKSPACE_ID, token),
    ])
      .then(([s, t, p, d]) => {
        setSummary(s);
        setTimeseries(t);
        setTopProducts(p);
        setDistribution(d);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [days]);

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Loading analytics...</div>;
  }

  const maxRevenue = Math.max(
    ...timeseries.map((p) => parseFloat(p.revenue) || 0),
    1
  );

  return (
    <div>
      {/* Period selector */}
      <div className="flex gap-2 mb-6">
        {[7, 14, 30, 90].map((d) => (
          <button
            key={d}
            onClick={() => setDays(d)}
            className={`px-3 py-1.5 text-sm rounded-md ${
              days === d
                ? "bg-blue-100 text-blue-700 font-medium"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            {d}d
          </button>
        ))}
      </div>

      {/* KPI cards */}
      {summary && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-xs text-gray-500 uppercase">Revenue</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              ${summary.total_revenue}
            </p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-xs text-gray-500 uppercase">Orders</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {summary.total_orders}
            </p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-xs text-gray-500 uppercase">AOV</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              ${summary.average_order_value}
            </p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-xs text-gray-500 uppercase">Return Rate</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {(summary.return_rate * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* Revenue chart (simple bar chart) */}
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 mb-4">Revenue Trend</h3>
          {timeseries.length > 0 ? (
            <div className="flex items-end gap-1 h-40">
              {timeseries.map((point) => {
                const height =
                  ((parseFloat(point.revenue) || 0) / maxRevenue) * 100;
                return (
                  <div
                    key={point.date}
                    className="flex-1 group relative"
                  >
                    <div
                      className="bg-blue-500 rounded-t hover:bg-blue-600 transition-colors"
                      style={{ height: `${Math.max(height, 2)}%` }}
                    />
                    <div className="hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap">
                      {point.date}: ${point.revenue} ({point.order_count} orders)
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No data for this period</p>
          )}
        </div>

        {/* Order status distribution */}
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 mb-4">Order Distribution</h3>
          {distribution.length > 0 ? (
            <div className="space-y-3">
              {distribution.map((d) => (
                <div key={d.status}>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-700">{d.status.replace(/_/g, " ")}</span>
                    <span className="text-gray-500">
                      {d.count} ({d.percentage}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${d.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No order data</p>
          )}
        </div>
      </div>

      {/* Top products */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h3 className="font-semibold text-gray-900">Top Products</h3>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Product</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Revenue</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Quantity</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {topProducts.map((product, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    {product.main_image_url && (
                      <img
                        src={product.main_image_url}
                        alt=""
                        className="w-8 h-8 rounded object-cover"
                      />
                    )}
                    <span className="text-sm text-gray-900">{product.title}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm font-medium text-gray-900">
                  ${product.total_revenue}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {product.total_quantity}
                </td>
              </tr>
            ))}
            {topProducts.length === 0 && (
              <tr>
                <td colSpan={3} className="px-4 py-6 text-center text-gray-500">
                  No product data yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
