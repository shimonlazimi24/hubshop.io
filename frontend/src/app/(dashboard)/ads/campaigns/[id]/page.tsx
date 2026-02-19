"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  getCampaign,
  updateCampaignStatus,
  type CampaignDetail,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

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
    } catch (err) {
      console.error(err);
    } finally {
      setToggling(false);
    }
  }

  if (loading) return <div className="text-center py-8 text-gray-500">Loading...</div>;
  if (!campaign) return <div className="text-center py-8 text-gray-500">Campaign not found</div>;

  return (
    <div>
      <button onClick={() => router.back()} className="text-sm text-blue-600 hover:underline mb-4">
        Back
      </button>

      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{campaign.campaign_name}</h2>
            <p className="text-sm text-gray-500 mt-1">ID: {campaign.platform_campaign_id}</p>
          </div>
          <button
            onClick={handleToggleStatus}
            disabled={toggling}
            className={`px-4 py-2 text-sm font-medium rounded-md disabled:opacity-50 ${
              campaign.operation_status === "ENABLE"
                ? "bg-red-50 text-red-700 hover:bg-red-100"
                : "bg-green-50 text-green-700 hover:bg-green-100"
            }`}
          >
            {toggling ? "Updating..." : campaign.operation_status === "ENABLE" ? "Disable" : "Enable"}
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div>
            <p className="text-xs text-gray-500 uppercase">Objective</p>
            <p className="text-sm font-medium mt-1">{campaign.objective_type?.replace(/_/g, " ") || "-"}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Status</p>
            <p className="text-sm font-medium mt-1">{campaign.operation_status}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Budget</p>
            <p className="text-sm font-medium mt-1">
              {campaign.budget ? `$${campaign.budget}` : "-"}
              {campaign.budget_mode && (
                <span className="text-xs text-gray-400 ml-1">
                  ({campaign.budget_mode === "BUDGET_MODE_DAY" ? "daily" : "total"})
                </span>
              )}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Secondary Status</p>
            <p className="text-sm font-medium mt-1">{campaign.secondary_status || "-"}</p>
          </div>
        </div>
      </div>

      {campaign.detail_json && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <button
            onClick={() => setShowJson(!showJson)}
            className="text-sm text-blue-600 hover:underline"
          >
            {showJson ? "Hide" : "Show"} Raw JSON
          </button>
          {showJson && (
            <pre className="mt-4 p-4 bg-gray-50 rounded text-xs overflow-auto max-h-96">
              {JSON.stringify(campaign.detail_json, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
