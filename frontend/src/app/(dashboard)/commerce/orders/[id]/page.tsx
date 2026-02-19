"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  getOrder,
  getOrderTimeline,
  shipPackage,
  type OrderDetail,
  type TimelineEvent,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export default function OrderDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showShipForm, setShowShipForm] = useState(false);
  const [shipProvider, setShipProvider] = useState("");
  const [trackingNumber, setTrackingNumber] = useState("");

  const token = getAccessToken();

  useEffect(() => {
    if (!token || !params.id) return;
    const orderId = params.id as string;

    Promise.all([
      getOrder(orderId, token),
      getOrderTimeline(orderId, token),
    ])
      .then(([o, t]) => {
        setOrder(o);
        setTimeline(t);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [params.id]);

  async function handleShip() {
    if (!token || !order) return;
    try {
      await shipPackage(
        {
          order_id: order.id,
          shipping_provider: shipProvider,
          tracking_number: trackingNumber,
        },
        token
      );
      // Refresh order
      const updated = await getOrder(order.id, token);
      setOrder(updated);
      setShowShipForm(false);
      setShipProvider("");
      setTrackingNumber("");
    } catch (err) {
      console.error("Failed to ship:", err);
    }
  }

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Loading order...</div>;
  }

  if (!order) {
    return <div className="text-center py-8 text-gray-500">Order not found</div>;
  }

  return (
    <div>
      <button
        onClick={() => router.back()}
        className="text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        &larr; Back to orders
      </button>

      {/* Order header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold text-gray-900">
              Order {order.platform_order_id}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Placed {new Date(order.created_at).toLocaleString()}
            </p>
          </div>
          <span
            className={`px-3 py-1 text-sm rounded-full font-medium ${
              order.status === "completed" || order.status === "delivered"
                ? "bg-green-100 text-green-800"
                : order.status === "cancelled"
                  ? "bg-red-100 text-red-800"
                  : "bg-yellow-100 text-yellow-800"
            }`}
          >
            {order.status.replace(/_/g, " ")}
          </span>
        </div>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-gray-500">Total</p>
            <p className="text-lg font-semibold text-gray-900">
              {order.currency} {order.total_amount}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Items</p>
            <p className="text-lg font-semibold text-gray-900">{order.item_count}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Fulfillment</p>
            <p className="text-lg font-semibold text-gray-900">
              {order.fulfillment_type || "Standard"}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">RTS SLA</p>
            <p className="text-lg font-semibold text-gray-900">
              {order.rts_sla ? new Date(order.rts_sla).toLocaleDateString() : "-"}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Line items */}
        <div className="col-span-2">
          <div className="bg-white rounded-lg border border-gray-200 mb-6">
            <div className="p-4 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900">Line Items</h3>
            </div>
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 text-left">
                  <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Product</th>
                  <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Qty</th>
                  <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Price</th>
                  <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {order.line_items.map((item) => (
                  <tr key={item.id}>
                    <td className="px-4 py-3 text-sm text-gray-900">{item.product_name}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{item.quantity}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{item.unit_price}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 font-medium">{item.total_price}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Packages */}
          <div className="bg-white rounded-lg border border-gray-200 mb-6">
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">
                Packages ({order.packages.length})
              </h3>
              {order.status === "awaiting_shipment" && (
                <button
                  onClick={() => setShowShipForm(!showShipForm)}
                  className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Ship Package
                </button>
              )}
            </div>

            {showShipForm && (
              <div className="p-4 border-b border-gray-200 bg-gray-50">
                <div className="flex gap-3">
                  <input
                    type="text"
                    placeholder="Shipping provider"
                    value={shipProvider}
                    onChange={(e) => setShipProvider(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                  <input
                    type="text"
                    placeholder="Tracking number"
                    value={trackingNumber}
                    onChange={(e) => setTrackingNumber(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                  <button
                    onClick={handleShip}
                    disabled={!shipProvider || !trackingNumber}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm disabled:opacity-50"
                  >
                    Confirm
                  </button>
                </div>
              </div>
            )}

            <div className="divide-y divide-gray-200">
              {order.packages.map((pkg) => (
                <div key={pkg.id} className="p-4 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {pkg.platform_package_id}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {pkg.shipping_provider || "N/A"} &middot;{" "}
                      {pkg.tracking_number || "No tracking"}
                    </p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      pkg.status === "delivered"
                        ? "bg-green-100 text-green-800"
                        : "bg-blue-100 text-blue-800"
                    }`}
                  >
                    {pkg.status}
                  </span>
                </div>
              ))}
              {order.packages.length === 0 && (
                <p className="p-4 text-sm text-gray-500">No packages yet</p>
              )}
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div>
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900">Timeline</h3>
            </div>
            <div className="p-4">
              {timeline.length > 0 ? (
                <div className="space-y-4">
                  {timeline.map((event, i) => (
                    <div key={event.id} className="flex gap-3">
                      <div className="flex flex-col items-center">
                        <div className="w-3 h-3 bg-blue-500 rounded-full" />
                        {i < timeline.length - 1 && (
                          <div className="w-0.5 h-full bg-gray-200 mt-1" />
                        )}
                      </div>
                      <div className="pb-4">
                        <p className="text-sm font-medium text-gray-900">
                          {event.to_status.replace(/_/g, " ")}
                        </p>
                        {event.from_status && (
                          <p className="text-xs text-gray-500">
                            from {event.from_status.replace(/_/g, " ")}
                          </p>
                        )}
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(event.occurred_at).toLocaleString()} &middot; {event.source}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No timeline events</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
