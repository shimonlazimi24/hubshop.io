"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  listOrders,
  listShops,
  syncShops,
  type OrderSummary,
  type PaginatedResponse,
  type Shop,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { useCommerceWebSocket, type CommerceWSMessage } from "@/hooks/useCommerceWebSocket";

// TODO: Get workspace ID from context/store
const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_COLORS: Record<string, string> = {
  awaiting_shipment: "bg-yellow-100 text-yellow-800",
  in_transit: "bg-blue-100 text-blue-800",
  delivered: "bg-green-100 text-green-800",
  completed: "bg-green-100 text-green-800",
  cancelled: "bg-red-100 text-red-800",
  unpaid: "bg-gray-100 text-gray-800",
};

export default function CommerceOrdersPage() {
  const [shops, setShops] = useState<Shop[]>([]);
  const [orders, setOrders] = useState<PaginatedResponse<OrderSummary> | null>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [page, setPage] = useState(1);
  const [liveUpdates, setLiveUpdates] = useState<string[]>([]);

  const token = getAccessToken();

  useCommerceWebSocket({
    workspaceId: WORKSPACE_ID,
    token,
    onMessage: (msg: CommerceWSMessage) => {
      if (msg.type === "order_status_change") {
        setLiveUpdates((prev) => [String(msg.order_id), ...prev.slice(0, 9)]);
        loadOrders();
      }
    },
  });

  useEffect(() => {
    loadShops();
    loadOrders();
  }, [statusFilter, page]);

  function loadShops() {
    if (!token) return;
    listShops(WORKSPACE_ID, token).then(setShops).catch(console.error);
  }

  function loadOrders() {
    if (!token) return;
    setLoading(true);
    listOrders(WORKSPACE_ID, token, {
      status_filter: statusFilter || undefined,
      page,
    })
      .then(setOrders)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleSyncShops() {
    if (!token) return;
    await syncShops(WORKSPACE_ID, token);
    loadShops();
  }

  if (shops.length === 0 && !loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
        <p className="text-gray-500 text-lg mb-4">No shops connected yet</p>
        <p className="text-gray-400 mb-6">
          Connect a TikTok Shop account first, then sync your shops.
        </p>
        <div className="flex gap-3 justify-center">
          <Link
            href="/connect"
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
          >
            Connect Account
          </Link>
          <button
            onClick={handleSyncShops}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Sync Shops
          </button>
        </div>
      </div>
    );
  }

  const STATUS_TABS = [
    { value: "", label: "All" },
    { value: "awaiting_shipment", label: "Awaiting Shipment" },
    { value: "in_transit", label: "In Transit" },
    { value: "delivered", label: "Delivered" },
    { value: "completed", label: "Completed" },
    { value: "cancelled", label: "Cancelled" },
  ];

  return (
    <div>
      {/* Status tabs */}
      <div className="flex gap-2 mb-4">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.value}
            onClick={() => {
              setStatusFilter(tab.value);
              setPage(1);
            }}
            className={`px-3 py-1.5 text-sm rounded-md ${
              statusFilter === tab.value
                ? "bg-blue-100 text-blue-700 font-medium"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Orders table */}
      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Order ID</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Total</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Items</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">SLA</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {orders?.items.map((order) => {
              const isLive = liveUpdates.includes(order.id);
              const slaColor = order.rts_sla
                ? new Date(order.rts_sla) < new Date()
                  ? "text-red-600"
                  : new Date(order.rts_sla).getTime() - Date.now() < 86400000
                    ? "text-yellow-600"
                    : "text-green-600"
                : "";

              return (
                <tr
                  key={order.id}
                  className={`hover:bg-gray-50 ${isLive ? "bg-blue-50" : ""}`}
                >
                  <td className="px-4 py-3">
                    <Link
                      href={`/commerce/orders/${order.id}`}
                      className="text-sm font-medium text-blue-600 hover:underline"
                    >
                      {order.platform_order_id}
                    </Link>
                    {isLive && (
                      <span className="ml-2 inline-block w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        STATUS_COLORS[order.status] || "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {order.status.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {order.currency} {order.total_amount}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{order.item_count}</td>
                  <td className={`px-4 py-3 text-sm ${slaColor}`}>
                    {order.rts_sla
                      ? new Date(order.rts_sla).toLocaleDateString()
                      : "-"}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {new Date(order.created_at).toLocaleDateString()}
                  </td>
                </tr>
              );
            })}
            {!loading && orders?.items.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  No orders found
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {orders && orders.total_pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Page {orders.page} of {orders.total_pages} ({orders.total} total)
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
                onClick={() => setPage((p) => Math.min(orders.total_pages, p + 1))}
                disabled={page >= orders.total_pages}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {loading && (
        <div className="text-center py-8 text-gray-500">Loading orders...</div>
      )}
    </div>
  );
}
