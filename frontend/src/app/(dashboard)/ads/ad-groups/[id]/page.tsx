"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowLeft, DollarSign, Target, Crosshair, Layers, TrendingUp, AlertTriangle } from "lucide-react";

import {
  getAdGroup,
  updateAdGroupStatus,
  type AdGroupDetail,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
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

export default function AdGroupDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [adGroup, setAdGroup] = useState<AdGroupDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);
  const [showJson, setShowJson] = useState(false);
  const [showTargeting, setShowTargeting] = useState(false);

  const token = getAccessToken();

  useEffect(() => {
    if (!token || !id) return;
    setLoading(true);
    getAdGroup(id, token)
      .then(setAdGroup)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  async function handleToggleStatus() {
    if (!token || !adGroup) return;
    setToggling(true);
    try {
      const newStatus = adGroup.operation_status === "ENABLE" ? "DISABLE" : "ENABLE";
      const updated = await updateAdGroupStatus(adGroup.id, newStatus, token);
      setAdGroup(updated);
      toast.success(`Ad group ${newStatus === "ENABLE" ? "enabled" : "paused"}`);
    } catch {
      toast.error("Failed to update ad group status");
    } finally {
      setToggling(false);
    }
  }

  if (loading) return <div className="text-center py-8 text-gray-500">Loading...</div>;
  if (!adGroup) return <div className="text-center py-8 text-gray-500">Ad group not found</div>;

  return (
    <>
      <PageHeader
        title={adGroup.adgroup_name}
        description={`ID: ${adGroup.platform_adgroup_id}`}
        actions={
          <div className="flex items-center gap-3">
            <StatusBadge variant={mapStatus(adGroup.operation_status)} label={mapStatusLabel(adGroup.operation_status)} />
            <button
              onClick={handleToggleStatus}
              disabled={toggling}
              className={`px-4 py-2 text-sm font-medium rounded-lg disabled:opacity-50 transition-colors ${
                adGroup.operation_status === "ENABLE"
                  ? "bg-danger/10 text-danger hover:bg-danger/20"
                  : "bg-success/10 text-success hover:bg-success/20"
              }`}
            >
              {toggling ? "Updating..." : adGroup.operation_status === "ENABLE" ? "Pause" : "Enable"}
            </button>
          </div>
        }
      />
      <button onClick={() => router.back()} className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4 transition-colors">
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to ad groups
      </button>

      <PageShell
        header={
          <MetricBar>
            <MetricCard
              label="Placement"
              value={adGroup.placement_type?.replace(/_/g, " ") || "Auto"}
              icon={Layers}
              iconColor="text-coral"
            />
            <MetricCard
              label="Bid"
              value={adGroup.bid_amount ? `$${adGroup.bid_amount}` : "-"}
              icon={DollarSign}
              iconColor="text-success"
            />
            <MetricCard
              label="Budget"
              value={adGroup.budget ? `$${adGroup.budget}` : "-"}
              icon={DollarSign}
              iconColor="text-info"
            />
            <MetricCard
              label="Optimization Goal"
              value={adGroup.optimization_goal?.replace(/_/g, " ") || "-"}
              icon={Crosshair}
              iconColor="text-purple"
            />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="Bid Efficiency"
              description="Current bid is within the recommended range for this audience segment."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Targeting Tip"
              description="Expanding age range to 18-34 could increase reach by 40% with minimal CPA impact."
              variant="warning"
            />
          </InsightPanel>
        }
      >
        {/* Targeting Configuration */}
        {adGroup.targeting_json && (
          <div className="rounded-xl border border-gray-100 bg-white p-5 mb-6">
            <button
              onClick={() => setShowTargeting(!showTargeting)}
              className="text-sm font-medium text-coral hover:text-coral-dark transition-colors"
            >
              <span className="flex items-center gap-1.5">
                <Target className="h-4 w-4" />
                {showTargeting ? "Hide" : "Show"} Targeting Configuration
              </span>
            </button>
            {showTargeting && (
              <pre className="mt-4 p-4 bg-gray-50 rounded-lg text-xs overflow-auto max-h-96">
                {JSON.stringify(adGroup.targeting_json, null, 2)}
              </pre>
            )}
          </div>
        )}

        {/* Raw JSON */}
        {adGroup.detail_json && (
          <div className="rounded-xl border border-gray-100 bg-white p-5">
            <button
              onClick={() => setShowJson(!showJson)}
              className="text-sm font-medium text-coral hover:text-coral-dark transition-colors"
            >
              {showJson ? "Hide" : "Show"} Raw JSON
            </button>
            {showJson && (
              <pre className="mt-4 p-4 bg-gray-50 rounded-lg text-xs overflow-auto max-h-96">
                {JSON.stringify(adGroup.detail_json, null, 2)}
              </pre>
            )}
          </div>
        )}
      </PageShell>
    </>
  );
}
