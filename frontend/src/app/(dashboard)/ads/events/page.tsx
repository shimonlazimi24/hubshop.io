"use client";

import { useState } from "react";
import { Activity, Send, Eye, ShoppingCart, CreditCard, UserPlus } from "lucide-react";
import { cn } from "@/lib/utils";

interface ServerEvent {
  id: string;
  event_type: string;
  timestamp: string;
  user_data_hashed: string;
  pixel_id: string;
  event_source: string;
  properties: Record<string, string | number>;
}

const EVENT_ICONS: Record<string, typeof Activity> = {
  PageView: Eye,
  AddToCart: ShoppingCart,
  Purchase: CreditCard,
  CompleteRegistration: UserPlus,
  SubmitForm: Send,
};

const EVENT_COLORS: Record<string, string> = {
  PageView: "bg-blue-100 text-blue-800",
  AddToCart: "bg-orange-100 text-orange-800",
  Purchase: "bg-green-100 text-green-800",
  CompleteRegistration: "bg-purple-100 text-purple-800",
  SubmitForm: "bg-cyan-100 text-cyan-800",
};

const MOCK_EVENTS: ServerEvent[] = [
  { id: "evt-1", event_type: "Purchase", timestamp: "2026-02-20T10:45:00Z", user_data_hashed: "a1b2c3...f8e9", pixel_id: "px-001", event_source: "server", properties: { currency: "USD", value: 89.99 } },
  { id: "evt-2", event_type: "AddToCart", timestamp: "2026-02-20T10:44:30Z", user_data_hashed: "d4e5f6...c7b8", pixel_id: "px-001", event_source: "server", properties: { currency: "USD", value: 34.99 } },
  { id: "evt-3", event_type: "PageView", timestamp: "2026-02-20T10:44:15Z", user_data_hashed: "g7h8i9...a1b2", pixel_id: "px-001", event_source: "server", properties: { page: "/products/123" } },
  { id: "evt-4", event_type: "CompleteRegistration", timestamp: "2026-02-20T10:43:00Z", user_data_hashed: "j0k1l2...d3e4", pixel_id: "px-002", event_source: "server", properties: {} },
  { id: "evt-5", event_type: "Purchase", timestamp: "2026-02-20T10:42:30Z", user_data_hashed: "m3n4o5...f6g7", pixel_id: "px-001", event_source: "server", properties: { currency: "USD", value: 156.00 } },
  { id: "evt-6", event_type: "PageView", timestamp: "2026-02-20T10:42:00Z", user_data_hashed: "p6q7r8...h9i0", pixel_id: "px-001", event_source: "server", properties: { page: "/collections/sale" } },
  { id: "evt-7", event_type: "AddToCart", timestamp: "2026-02-20T10:41:45Z", user_data_hashed: "s9t0u1...j2k3", pixel_id: "px-002", event_source: "server", properties: { currency: "USD", value: 24.99 } },
  { id: "evt-8", event_type: "SubmitForm", timestamp: "2026-02-20T10:41:00Z", user_data_hashed: "v4w5x6...l7m8", pixel_id: "px-001", event_source: "server", properties: { form: "newsletter" } },
  { id: "evt-9", event_type: "Purchase", timestamp: "2026-02-20T10:40:30Z", user_data_hashed: "y7z8a9...n0o1", pixel_id: "px-001", event_source: "server", properties: { currency: "USD", value: 45.00 } },
  { id: "evt-10", event_type: "PageView", timestamp: "2026-02-20T10:40:00Z", user_data_hashed: "b2c3d4...p5q6", pixel_id: "px-002", event_source: "server", properties: { page: "/checkout" } },
];

const STATS = {
  total_today: 1_247,
  purchases: 89,
  add_to_cart: 312,
  page_views: 846,
};

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export default function EventTrackingPage() {
  const [events] = useState<ServerEvent[]>(MOCK_EVENTS);

  return (
    <div className="max-w-6xl">
      {/* Stats Bar */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="rounded-xl border border-gray-100 bg-white p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 border border-blue-100">
              <Activity className="h-[18px] w-[18px] text-blue-500" />
            </div>
          </div>
          <p className="text-2xl font-semibold text-gray-900">{formatNumber(STATS.total_today)}</p>
          <p className="text-xs text-gray-400 mt-1">Events Today</p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-green-50 border border-green-100">
              <CreditCard className="h-[18px] w-[18px] text-green-500" />
            </div>
          </div>
          <p className="text-2xl font-semibold text-gray-900">{STATS.purchases}</p>
          <p className="text-xs text-gray-400 mt-1">Purchases</p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-orange-50 border border-orange-100">
              <ShoppingCart className="h-[18px] w-[18px] text-orange-500" />
            </div>
          </div>
          <p className="text-2xl font-semibold text-gray-900">{STATS.add_to_cart}</p>
          <p className="text-xs text-gray-400 mt-1">Add to Cart</p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-purple/5 border border-purple/10">
              <Eye className="h-[18px] w-[18px] text-purple" />
            </div>
          </div>
          <p className="text-2xl font-semibold text-gray-900">{STATS.page_views}</p>
          <p className="text-xs text-gray-400 mt-1">Page Views</p>
        </div>
      </div>

      {/* Recent Events Table */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Recent Server-Side Events</h3>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Event Type</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Timestamp</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">User Data</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Pixel</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Properties</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {events.map((event) => {
              const Icon = EVENT_ICONS[event.event_type] || Activity;
              const colorClass = EVENT_COLORS[event.event_type] || "bg-gray-100 text-gray-800";
              return (
                <tr key={event.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <span className={cn("inline-flex items-center gap-1 px-2 py-1 text-xs rounded-full", colorClass)}>
                      <Icon className="h-3 w-3" />
                      {event.event_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="px-4 py-3">
                    <code className="text-xs font-mono text-gray-500 bg-gray-50 px-1.5 py-0.5 rounded">
                      {event.user_data_hashed}
                    </code>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{event.pixel_id}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(event.properties).map(([key, val]) => (
                        <span key={key} className="text-xs bg-gray-50 px-1.5 py-0.5 rounded text-gray-500">
                          {key}: {val}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {events.length === 0 && (
          <div className="px-4 py-8 text-center text-gray-500">
            No events tracked yet
          </div>
        )}
      </div>
    </div>
  );
}
