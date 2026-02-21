"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowLeft, DollarSign, Package, Clock, Truck } from "lucide-react";
import {
  getOrder,
  getOrderTimeline,
  shipPackage,
  type OrderDetail,
  type TimelineEvent,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { DataTable, type Column } from "@/components/ui/data-table";
import { toast } from "@/lib/toast-store";

const STATUS_MAP: Record<string, StatusVariant> = {
  completed: "completed",
  delivered: "completed",
  in_transit: "syncing",
  awaiting_shipment: "warning",
  cancelled: "error",
  unpaid: "draft",
};

interface LineItem {
  id: string;
  product_name: string;
  quantity: number;
  unit_price: string;
  total_price: string;
}

const lineItemColumns: Column<LineItem>[] = [
  {
    key: "product",
    header: "Product",
    render: (row) => <span className="text-sm font-medium text-gray-900">{row.product_name}</span>,
  },
  {
    key: "qty",
    header: "Qty",
    render: (row) => <span className="text-sm text-gray-600">{row.quantity}</span>,
  },
  {
    key: "price",
    header: "Price",
    render: (row) => <span className="text-sm text-gray-600">{row.unit_price}</span>,
  },
  {
    key: "total",
    header: "Total",
    render: (row) => <span className="text-sm font-medium text-gray-900">{row.total_price}</span>,
  },
];

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
      toast.success("Package shipped successfully");
      const updated = await getOrder(order.id, token);
      setOrder(updated);
      setShowShipForm(false);
      setShipProvider("");
      setTrackingNumber("");
    } catch {
      toast.error("Failed to ship package");
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
        className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" /> Back to orders
      </button>

      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Order {order.platform_order_id}</h2>
          <p className="text-sm text-gray-500">Placed {new Date(order.created_at).toLocaleString()}</p>
        </div>
        <StatusBadge
          variant={STATUS_MAP[order.status] || "draft"}
          label={order.status.replace(/_/g, " ")}
        />
      </div>

      <PageShell
        header={
          <MetricBar>
            <MetricCard
              label="Total"
              value={`${order.currency} ${order.total_amount}`}
              icon={DollarSign}
              iconColor="text-success"
            />
            <MetricCard
              label="Items"
              value={order.item_count}
              icon={Package}
              iconColor="text-coral"
            />
            <MetricCard
              label="Fulfillment"
              value={order.fulfillment_type || "Standard"}
              icon={Truck}
              iconColor="text-info"
            />
            <MetricCard
              label="RTS SLA"
              value={order.rts_sla ? new Date(order.rts_sla).toLocaleDateString() : "-"}
              icon={Clock}
              iconColor="text-warning"
            />
          </MetricBar>
        }
      >
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Line Items */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Line Items</h3>
              <DataTable
                columns={lineItemColumns}
                data={order.line_items}
                keyExtractor={(row) => row.id}
                emptyTitle="No line items"
              />
            </div>

            {/* Packages */}
            <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)]">
              <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
                <h3 className="text-sm font-semibold text-gray-900">
                  Packages ({order.packages.length})
                </h3>
                {order.status === "awaiting_shipment" && (
                  <button
                    onClick={() => setShowShipForm(!showShipForm)}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-coral px-3 py-1.5 text-xs font-medium text-white hover:bg-coral-dark transition-colors"
                  >
                    Ship Package
                  </button>
                )}
              </div>

              {showShipForm && (
                <div className="px-5 py-4 border-b border-gray-100 bg-gray-50/50">
                  <div className="flex gap-3">
                    <input
                      type="text"
                      placeholder="Shipping provider"
                      value={shipProvider}
                      onChange={(e) => setShipProvider(e.target.value)}
                      className="flex-1 h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
                    />
                    <input
                      type="text"
                      placeholder="Tracking number"
                      value={trackingNumber}
                      onChange={(e) => setTrackingNumber(e.target.value)}
                      className="flex-1 h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
                    />
                    <button
                      onClick={handleShip}
                      disabled={!shipProvider || !trackingNumber}
                      className="inline-flex items-center rounded-lg bg-coral px-4 py-2 text-sm font-medium text-white hover:bg-coral-dark transition-colors disabled:opacity-50"
                    >
                      Confirm
                    </button>
                  </div>
                </div>
              )}

              <div className="divide-y divide-gray-50">
                {order.packages.map((pkg) => (
                  <div key={pkg.id} className="flex items-center justify-between px-5 py-3">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{pkg.platform_package_id}</p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {pkg.shipping_provider || "N/A"} &middot; {pkg.tracking_number || "No tracking"}
                      </p>
                    </div>
                    <StatusBadge
                      variant={pkg.status === "delivered" ? "completed" : "syncing"}
                      label={pkg.status}
                    />
                  </div>
                ))}
                {order.packages.length === 0 && (
                  <p className="px-5 py-4 text-sm text-gray-500">No packages yet</p>
                )}
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div>
            <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)]">
              <div className="px-5 py-4 border-b border-gray-100">
                <h3 className="text-sm font-semibold text-gray-900">Timeline</h3>
              </div>
              <div className="p-5">
                {timeline.length > 0 ? (
                  <div className="space-y-4">
                    {timeline.map((event, i) => (
                      <div key={event.id} className="flex gap-3">
                        <div className="flex flex-col items-center">
                          <div className="w-2.5 h-2.5 bg-coral rounded-full mt-1" />
                          {i < timeline.length - 1 && (
                            <div className="w-0.5 flex-1 bg-gray-100 mt-1" />
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
      </PageShell>
    </div>
  );
}
