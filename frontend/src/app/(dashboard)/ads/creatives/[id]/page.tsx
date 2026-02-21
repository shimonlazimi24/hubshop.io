"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowLeft, Image, FileText, Activity, TrendingUp, AlertTriangle } from "lucide-react";

import { getAd, updateAdStatus, type AdDetail } from "@/lib/api";
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

export default function AdDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [ad, setAd] = useState<AdDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);
  const [showJson, setShowJson] = useState(false);

  const token = getAccessToken();

  useEffect(() => {
    if (!token || !id) return;
    setLoading(true);
    getAd(id, token)
      .then(setAd)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  async function handleToggleStatus() {
    if (!token || !ad) return;
    setToggling(true);
    try {
      const newStatus = ad.operation_status === "ENABLE" ? "DISABLE" : "ENABLE";
      const updated = await updateAdStatus(ad.id, newStatus, token);
      setAd(updated);
      toast.success(`Ad ${newStatus === "ENABLE" ? "enabled" : "paused"}`);
    } catch {
      toast.error("Failed to update ad status");
    } finally {
      setToggling(false);
    }
  }

  if (loading) return <div className="text-center py-8 text-gray-500">Loading...</div>;
  if (!ad) return <div className="text-center py-8 text-gray-500">Ad not found</div>;

  return (
    <>
      <PageHeader
        title={ad.ad_name}
        description={`ID: ${ad.platform_ad_id}`}
        actions={
          <div className="flex items-center gap-3">
            <StatusBadge variant={mapStatus(ad.operation_status)} label={mapStatusLabel(ad.operation_status)} />
            <button
              onClick={handleToggleStatus}
              disabled={toggling}
              className={`px-4 py-2 text-sm font-medium rounded-lg disabled:opacity-50 transition-colors ${
                ad.operation_status === "ENABLE"
                  ? "bg-danger/10 text-danger hover:bg-danger/20"
                  : "bg-success/10 text-success hover:bg-success/20"
              }`}
            >
              {toggling ? "Updating..." : ad.operation_status === "ENABLE" ? "Pause Ad" : "Enable Ad"}
            </button>
          </div>
        }
      />
      <button onClick={() => router.back()} className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4 transition-colors">
        <ArrowLeft className="h-3.5 w-3.5" />
        Back
      </button>

      <PageShell
        header={
          <MetricBar>
            <MetricCard label="Format" value={ad.ad_format?.replace(/_/g, " ") || "-"} icon={Image} iconColor="text-coral" />
            <MetricCard label="CTA" value={ad.call_to_action || "-"} icon={FileText} iconColor="text-purple" />
            <MetricCard label="Status" value={mapStatusLabel(ad.operation_status)} icon={Activity} iconColor="text-info" />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="Creative Performance"
              description="This ad format typically achieves 15% higher CTR on TikTok."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Landing Page"
              description="Ensure your landing page is mobile-optimized for best conversion rates."
              variant="warning"
            />
          </InsightPanel>
        }
      >
        {/* Ad Details */}
        <div className="rounded-xl border border-gray-100 bg-white p-5 mb-6 shadow-[var(--shadow-card)]">
          {ad.ad_text && (
            <div className="mb-4">
              <p className="text-xs text-gray-500 uppercase font-medium mb-1">Ad Text</p>
              <p className="text-sm text-gray-900">{ad.ad_text}</p>
            </div>
          )}

          {ad.landing_page_url && (
            <div className="mb-4">
              <p className="text-xs text-gray-500 uppercase font-medium mb-1">Landing Page</p>
              <p className="text-sm text-coral truncate">{ad.landing_page_url}</p>
            </div>
          )}

          {ad.image_url && (
            <div>
              <p className="text-xs text-gray-500 uppercase font-medium mb-2">Creative Preview</p>
              <img src={ad.image_url} alt={ad.ad_name} className="max-w-sm rounded-lg border border-gray-100" />
            </div>
          )}
        </div>

        {/* Raw JSON */}
        {ad.detail_json && (
          <div className="rounded-xl border border-gray-100 bg-white p-5">
            <button
              onClick={() => setShowJson(!showJson)}
              className="text-sm font-medium text-coral hover:text-coral-dark transition-colors"
            >
              {showJson ? "Hide" : "Show"} Raw JSON
            </button>
            {showJson && (
              <pre className="mt-4 p-4 bg-gray-50 rounded-lg text-xs overflow-auto max-h-96">
                {JSON.stringify(ad.detail_json, null, 2)}
              </pre>
            )}
          </div>
        )}
      </PageShell>
    </>
  );
}
