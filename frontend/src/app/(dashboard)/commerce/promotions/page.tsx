"use client";

import { useEffect, useState } from "react";
import { listPromotions, type Promotion, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_COLORS: Record<string, string> = {
  ACTIVE: "bg-green-100 text-green-800",
  DRAFT: "bg-yellow-100 text-yellow-800",
  ENDED: "bg-gray-100 text-gray-800",
  CANCELLED: "bg-red-100 text-red-800",
};

export default function PromotionsPage() {
  const [data, setData] = useState<PaginatedResponse<Promotion> | null>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    listPromotions(WORKSPACE_ID, token, {
      status_filter: statusFilter || undefined,
      page,
    })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [statusFilter, page]);

  return (
    <div>
      <div className="flex items-center gap-4 mb-4">
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm"
        >
          <option value="">All Statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="DRAFT">Draft</option>
          <option value="ENDED">Ended</option>
        </select>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Title</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Discount</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Period</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data?.items.map((promo) => (
              <tr key={promo.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{promo.title}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{promo.promotion_type}</td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {promo.discount_value ? `${promo.discount_value}${promo.discount_type === "PERCENTAGE" ? "%" : ""}` : "-"}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${STATUS_COLORS[promo.status] || "bg-gray-100 text-gray-800"}`}>
                    {promo.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {promo.start_time ? new Date(promo.start_time).toLocaleDateString() : "-"}
                  {promo.end_time ? ` - ${new Date(promo.end_time).toLocaleDateString()}` : ""}
                </td>
              </tr>
            ))}
            {!loading && (!data || data.items.length === 0) && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">No promotions found</td></tr>
            )}
          </tbody>
        </table>

        {data && data.total_pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
            <p className="text-sm text-gray-500">Page {data.page} of {data.total_pages}</p>
            <div className="flex gap-2">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1} className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50">Previous</button>
              <button onClick={() => setPage(p => Math.min(data.total_pages, p + 1))} disabled={page >= data.total_pages} className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50">Next</button>
            </div>
          </div>
        )}
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Loading promotions...</div>}
    </div>
  );
}
