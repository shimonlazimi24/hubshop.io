"use client";

import { useEffect, useState } from "react";
import { Code, Activity, Copy, TrendingUp, AlertTriangle } from "lucide-react";
import { listPixels, getPixelCode, type Pixel, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { ActionMenu } from "@/components/ui/action-menu";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

export default function PixelsPage() {
  const [data, setData] = useState<PaginatedResponse<Pixel> | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPixel, setSelectedPixel] = useState<string | null>(null);
  const [pixelCode, setPixelCode] = useState<string | null>(null);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    listPixels(WORKSPACE_ID, token)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  async function handleGetCode(pixelId: string) {
    if (!token) return;
    setSelectedPixel(pixelId);
    try {
      const result = await getPixelCode(pixelId, token);
      setPixelCode(result.pixel_code);
      toast.success("Pixel code loaded");
    } catch {
      toast.error("Failed to load pixel code");
    }
  }

  const columns: Column<Pixel>[] = [
    {
      key: "name",
      header: "Name",
      sortable: true,
      render: (row) => <span className="text-sm font-medium text-gray-900">{row.name}</span>,
    },
    {
      key: "pixel_id",
      header: "Pixel ID",
      render: (row) => <code className="text-xs font-mono text-gray-600 bg-gray-50 px-1.5 py-0.5 rounded">{row.platform_pixel_id}</code>,
    },
    {
      key: "created",
      header: "Created",
      sortable: true,
      render: (row) => <span className="text-sm text-gray-500">{new Date(row.created_at).toLocaleDateString()}</span>,
    },
    {
      key: "actions",
      header: "",
      className: "w-12",
      render: (row) => (
        <ActionMenu
          items={[
            { label: "Get Code", icon: <Code className="h-4 w-4" />, onClick: () => handleGetCode(row.id) },
            { label: "Copy ID", icon: <Copy className="h-4 w-4" />, onClick: () => { navigator.clipboard.writeText(row.platform_pixel_id); toast.success("Pixel ID copied"); } },
          ]}
        />
      ),
    },
  ];

  return (
    <>
      <PageHeader title="Pixels" description="Manage your TikTok tracking pixels and get installation code" />
      <PageShell
        header={
          <MetricBar>
            <MetricCard label="Total Pixels" value={data?.total ?? 0} icon={Code} iconColor="text-coral" />
            <MetricCard label="Events Today" value="1,247" icon={Activity} iconColor="text-success" trend={{ value: 12, direction: "up", label: "vs yesterday" }} />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="Pixel Health"
              description="All pixels are firing correctly with 100% uptime in the last 24 hours."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Server-Side Events"
              description="Consider setting up Events API for more accurate tracking and better ad optimization."
              variant="warning"
              action={{ label: "Learn more", onClick: () => {} }}
            />
          </InsightPanel>
        }
      >
        <DataTable
          columns={columns}
          data={data?.items ?? []}
          keyExtractor={(row) => row.id}
          loading={loading}
          emptyTitle="No pixels found"
          emptyDescription="Create a TikTok pixel to start tracking conversions."
        />

        {selectedPixel && pixelCode && (
          <div className="mt-6 rounded-xl border border-gray-100 bg-white p-5 shadow-[var(--shadow-card)]">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-900">Pixel Code</h3>
              <button
                onClick={() => { navigator.clipboard.writeText(pixelCode); toast.success("Code copied to clipboard"); }}
                className="flex items-center gap-1.5 text-xs font-medium text-coral hover:text-coral-dark transition-colors"
              >
                <Copy className="h-3.5 w-3.5" />
                Copy
              </button>
            </div>
            <pre className="bg-gray-50 rounded-lg p-3 text-xs overflow-x-auto border border-gray-100">
              <code>{pixelCode}</code>
            </pre>
          </div>
        )}
      </PageShell>
    </>
  );
}
