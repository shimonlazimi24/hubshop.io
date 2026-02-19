"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  getAdGroup,
  updateAdGroupStatus,
  type AdGroupDetail,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

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
    } catch (err) {
      console.error(err);
    } finally {
      setToggling(false);
    }
  }

  if (loading) return <div className="text-center py-8 text-gray-500">Loading...</div>;
  if (!adGroup) return <div className="text-center py-8 text-gray-500">Ad group not found</div>;

  return (
    <div>
      <button onClick={() => router.back()} className="text-sm text-blue-600 hover:underline mb-4">
        Back
      </button>

      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{adGroup.adgroup_name}</h2>
            <p className="text-sm text-gray-500 mt-1">ID: {adGroup.platform_adgroup_id}</p>
          </div>
          <button
            onClick={handleToggleStatus}
            disabled={toggling}
            className={`px-4 py-2 text-sm font-medium rounded-md disabled:opacity-50 ${
              adGroup.operation_status === "ENABLE"
                ? "bg-red-50 text-red-700 hover:bg-red-100"
                : "bg-green-50 text-green-700 hover:bg-green-100"
            }`}
          >
            {toggling ? "Updating..." : adGroup.operation_status === "ENABLE" ? "Disable" : "Enable"}
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div>
            <p className="text-xs text-gray-500 uppercase">Status</p>
            <p className="text-sm font-medium mt-1">{adGroup.operation_status}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Placement</p>
            <p className="text-sm font-medium mt-1">{adGroup.placement_type?.replace(/_/g, " ") || "-"}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Bid</p>
            <p className="text-sm font-medium mt-1">
              {adGroup.bid_amount ? `$${adGroup.bid_amount}` : "-"}
              {adGroup.bid_type && <span className="text-xs text-gray-400 ml-1">({adGroup.bid_type})</span>}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Budget</p>
            <p className="text-sm font-medium mt-1">{adGroup.budget ? `$${adGroup.budget}` : "-"}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Optimization Goal</p>
            <p className="text-sm font-medium mt-1">{adGroup.optimization_goal?.replace(/_/g, " ") || "-"}</p>
          </div>
        </div>
      </div>

      {adGroup.targeting_json && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <button
            onClick={() => setShowTargeting(!showTargeting)}
            className="text-sm text-blue-600 hover:underline"
          >
            {showTargeting ? "Hide" : "Show"} Targeting Configuration
          </button>
          {showTargeting && (
            <pre className="mt-4 p-4 bg-gray-50 rounded text-xs overflow-auto max-h-96">
              {JSON.stringify(adGroup.targeting_json, null, 2)}
            </pre>
          )}
        </div>
      )}

      {adGroup.detail_json && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <button
            onClick={() => setShowJson(!showJson)}
            className="text-sm text-blue-600 hover:underline"
          >
            {showJson ? "Hide" : "Show"} Raw JSON
          </button>
          {showJson && (
            <pre className="mt-4 p-4 bg-gray-50 rounded text-xs overflow-auto max-h-96">
              {JSON.stringify(adGroup.detail_json, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
