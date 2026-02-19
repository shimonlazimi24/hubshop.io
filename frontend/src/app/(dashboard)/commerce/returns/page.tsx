"use client";

import { useEffect, useState } from "react";

import {
  approveReturn,
  listReturns,
  rejectReturn,
  type PaginatedResponse,
  type ReturnRequest,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  approved: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
  buyer_shipped: "bg-blue-100 text-blue-800",
  seller_received: "bg-blue-100 text-blue-800",
  refunded: "bg-green-100 text-green-800",
  closed: "bg-gray-100 text-gray-800",
};

export default function ReturnsPage() {
  const [returns, setReturns] = useState<PaginatedResponse<ReturnRequest> | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  const token = getAccessToken();

  useEffect(() => {
    loadReturns();
  }, [page]);

  function loadReturns() {
    if (!token) return;
    setLoading(true);
    listReturns(WORKSPACE_ID, token, { page })
      .then(setReturns)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleApprove(returnId: string) {
    if (!token) return;
    try {
      await approveReturn(returnId, token);
      loadReturns();
    } catch (err) {
      console.error("Failed to approve:", err);
    }
  }

  async function handleReject(returnId: string) {
    if (!token) return;
    const reason = prompt("Rejection reason (optional):");
    try {
      await rejectReturn(returnId, token, reason || undefined);
      loadReturns();
    } catch (err) {
      console.error("Failed to reject:", err);
    }
  }

  return (
    <div>
      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Return ID</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Reason</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Refund</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {returns?.items.map((ret) => (
              <tr key={ret.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-mono text-gray-600">
                  {ret.platform_return_id}
                </td>
                <td className="px-4 py-3 text-sm text-gray-900">
                  {ret.return_type.replace(/_/g, " ")}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      STATUS_COLORS[ret.status] || "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {ret.status.replace(/_/g, " ")}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600 max-w-[200px] truncate">
                  {ret.reason || "-"}
                </td>
                <td className="px-4 py-3 text-sm text-gray-900">
                  {ret.refund_amount || "-"}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {new Date(ret.created_at).toLocaleDateString()}
                </td>
                <td className="px-4 py-3">
                  {ret.status === "pending" && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleApprove(ret.id)}
                        className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => handleReject(ret.id)}
                        className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
            {!loading && returns?.items.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                  No return requests
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {returns && returns.total_pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Page {returns.page} of {returns.total_pages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => Math.min(returns.total_pages, p + 1))}
                disabled={page >= returns.total_pages}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Loading returns...</div>}
    </div>
  );
}
