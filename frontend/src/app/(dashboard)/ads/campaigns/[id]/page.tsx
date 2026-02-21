"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowLeft, DollarSign, Target, BarChart3, Activity, TrendingUp, AlertTriangle } from "lucide-react";

import {
  getCampaign,
  updateCampaignStatus,
  type CampaignDetail,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { ChartCard } from "@/components/ui/chart-card";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";

function mapStatus(status: string): StatusVariant {
  switch (status) {
    case "ENABLE": return "active";
    case "DISABLE": return "paused";
    case "DELETE": return "error";
    default: return "draft";
  }
}

function mapStatusLabel(status: string): string {
  switch (status) {
    case "ENABLE": return "Active";
    case "DISABLE": return "Paused";
    case "DELETE": return "Deleted";
    default: return status;
  }
}

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [campaign, setCampaign] = useState<CampaignDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);
  const [showJson, setShowJson] = useState(false);

  const token = getAccessToken();

  useEffect(() => {
    if (!token || !id) return;
    setLoading(true);
    getCampaign(id, token)
      .then(setCampaign)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  async function handleToggleStatus() {
    if (!token || !campaign) return;
    setToggling(true);
    try {
      const newStatus = campaign.operation_status === "ENABLE" ? "DISABLE" : "ENABLE";
      const updated = await updateCampaignStatus(campaign.id, newStatus, token);
      setCampaign(updated);
      toast.success(`Campaign ${newStatus === "ENABLE" ? "enabled" : "paused"}`);
    } catch {
      toast.error("Failed to update campaign status");
    } finally {
      setToggling(false);
    }
  }

  if (loading) return <div className="text-center py-8 text-gray-500">Loading...</div>;
  if (!campaign) return <div className="text-center py-8 text-gray-500">Campaign not found</div>;

  return (
    <>
      <PageHeader
        title={campaign.campaign_name}
        description={`ID: ${campaign.platform_campaign_id}`}
        actions={
          <div className="flex items-center gap-3">
            <StatusBadge variant={mapStatus(campaign.operation_status)} label={mapStatusLabel(campaign.operation_status)} />
            <button
              onClick={handleToggleStatus}
              disabled={toggling}
              className={`px-4 py-2 text-sm font-medium rounded-lg disabled:opacity-50 transition-colors ${
                campaign.operation_status === "ENABLE"
                  ? "bg-danger/10 text-danger hover:bg-danger/20"
                  : "bg-success/10 text-success hover:bg-success/20"
              }`}
            >
              {toggling ? "Updating..." : campaign.operation_status === "ENABLE" ? "Pause Campaign" : "Enable Campaign"}
            </button>
          </div>
        }
      />
      <button onClick={() => router.back()} className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4 transition-colors">
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to campaigns
      </button>

      <PageShell
        header={
          <MetricBar>
            <MetricCard
              label="Objective"
              value={campaign.objective_type?.replace(/_/g, " ") || "-"}
              icon={Target}
              iconColor="text-coral"
            />
            <MetricCard
              label="Budget"
              value={campaign.budget ? `$${campaign.budget}` : "-"}
              icon={DollarSign}
              iconColor="text-success"
            />
            <MetricCard
              label="Budget Mode"
              value={campaign.budget_mode === "BUDGET_MODE_DAY" ? "Daily" : campaign.budget_mode === "BUDGET_MODE_TOTAL" ? "Total" : "Infinite"}
              icon={BarChart3}
              iconColor="text-info"
            />
            <MetricCard
              label="Secondary Status"
              value={campaign.secondary_status || "None"}
              icon={Activity}
              iconColor="text-purple"
            />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="Performance Trend"
              description="This campaign's ROAS has improved 12% over the past 7 days."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Budget Recommendation"
              description="Consider increasing the daily budget by 15% to capture more conversions during peak hours."
              variant="warning"
            />
          </InsightPanel>
        }
      >
        {/* Performance Chart */}
        <ChartCard title="Performance Over Time" className="mb-6">
          <div className="flex items-center justify-center h-full text-sm text-gray-400">
            Chart data loads from the reporting API
          </div>
        </ChartCard>

        {/* Raw JSON */}
        {campaign.detail_json && (
          <div className="rounded-xl border border-gray-100 bg-white p-5">
            <button
              onClick={() => setShowJson(!showJson)}
              className="text-sm font-medium text-coral hover:text-coral-dark transition-colors"
            >
              {showJson ? "Hide" : "Show"} Raw JSON
            </button>
            {showJson && (
              <pre className="mt-4 p-4 bg-gray-50 rounded-lg text-xs overflow-auto max-h-96">
                {JSON.stringify(campaign.detail_json, null, 2)}
              </pre>
            )}
          </div>
        )}
      </PageShell>
    </>
  );
}
