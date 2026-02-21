"use client";

import { useState } from "react";
import { Activity, Send, Eye, ShoppingCart, CreditCard, UserPlus, TrendingUp, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";

interface ServerEvent {
  id: string;
  event_type: string;
  timestamp: string;
  user_data_hashed: string;
  pixel_id: string;
  event_source: string;
  properties: Record<string, string | number>;
}

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

const EVENT_VARIANT: Record<string, string> = {
  Purchase: "active",
  AddToCart: "warning",
  PageView: "syncing",
  CompleteRegistration: "completed",
  SubmitForm: "draft",
};

export default function EventTrackingPage() {
  const [events] = useState<ServerEvent[]>(MOCK_EVENTS);

  const columns: Column<ServerEvent>[] = [
    {
      key: "event_type",
      header: "Event Type",
      render: (row) => (
        <StatusBadge
          variant={(EVENT_VARIANT[row.event_type] || "draft") as "active" | "warning" | "syncing" | "completed" | "draft"}
          label={row.event_type}
        />
      ),
    },
    {
      key: "timestamp",
      header: "Timestamp",
      sortable: true,
      render: (row) => <span className="text-sm text-gray-500">{new Date(row.timestamp).toLocaleTimeString()}</span>,
    },
    {
      key: "user_data",
      header: "User Data",
      render: (row) => <code className="text-xs font-mono text-gray-500 bg-gray-50 px-1.5 py-0.5 rounded">{row.user_data_hashed}</code>,
    },
    {
      key: "pixel",
      header: "Pixel",
      render: (row) => <span className="text-sm text-gray-600">{row.pixel_id}</span>,
    },
    {
      key: "properties",
      header: "Properties",
      render: (row) => (
        <div className="flex flex-wrap gap-1">
          {Object.entries(row.properties).map(([key, val]) => (
            <span key={key} className="text-xs bg-gray-50 px-1.5 py-0.5 rounded text-gray-500">{key}: {val}</span>
          ))}
        </div>
      ),
    },
  ];

  return (
    <>
      <PageHeader title="Event Tracking" description="Server-side event monitoring and diagnostics" />
      <PageShell
        header={
          <MetricBar>
            <MetricCard label="Events Today" value={STATS.total_today.toLocaleString()} icon={Activity} iconColor="text-info" trend={{ value: 12, direction: "up", label: "vs yesterday" }} sparklineData={[800, 900, 1050, 1100, 1180, 1220, 1247]} />
            <MetricCard label="Purchases" value={STATS.purchases} icon={CreditCard} iconColor="text-success" trend={{ value: 8.5, direction: "up", label: "vs yesterday" }} />
            <MetricCard label="Add to Cart" value={STATS.add_to_cart} icon={ShoppingCart} iconColor="text-warning" />
            <MetricCard label="Page Views" value={STATS.page_views} icon={Eye} iconColor="text-purple" />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="Event Volume"
              description="Event volume is up 12% compared to yesterday. All pixels are firing correctly."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Data Quality"
              description="2 events are missing user_data fields. Review your server-side integration."
              variant="warning"
              action={{ label: "Review events", onClick: () => {} }}
            />
          </InsightPanel>
        }
      >
        <h2 className="text-sm font-semibold text-gray-900 mb-4">Recent Server-Side Events</h2>
        <DataTable
          columns={columns}
          data={events}
          keyExtractor={(row) => row.id}
          emptyTitle="No events tracked yet"
          emptyDescription="Events will appear here once your pixel starts firing."
        />
      </PageShell>
    </>
  );
}
