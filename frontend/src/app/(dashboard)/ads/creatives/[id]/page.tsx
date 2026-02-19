"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getAd, updateAdStatus, type AdDetail } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

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
    } catch (err) {
      console.error(err);
    } finally {
      setToggling(false);
    }
  }

  if (loading) return <div className="text-center py-8 text-gray-500">Loading...</div>;
  if (!ad) return <div className="text-center py-8 text-gray-500">Ad not found</div>;

  return (
    <div>
      <button onClick={() => router.back()} className="text-sm text-blue-600 hover:underline mb-4">
        Back
      </button>

      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{ad.ad_name}</h2>
            <p className="text-sm text-gray-500 mt-1">ID: {ad.platform_ad_id}</p>
          </div>
          <button
            onClick={handleToggleStatus}
            disabled={toggling}
            className={`px-4 py-2 text-sm font-medium rounded-md disabled:opacity-50 ${
              ad.operation_status === "ENABLE"
                ? "bg-red-50 text-red-700 hover:bg-red-100"
                : "bg-green-50 text-green-700 hover:bg-green-100"
            }`}
          >
            {toggling ? "Updating..." : ad.operation_status === "ENABLE" ? "Disable" : "Enable"}
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6">
          <div>
            <p className="text-xs text-gray-500 uppercase">Format</p>
            <p className="text-sm font-medium mt-1">{ad.ad_format?.replace(/_/g, " ") || "-"}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Status</p>
            <p className="text-sm font-medium mt-1">{ad.operation_status}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase">Call to Action</p>
            <p className="text-sm font-medium mt-1">{ad.call_to_action || "-"}</p>
          </div>
        </div>

        {ad.ad_text && (
          <div className="mt-4">
            <p className="text-xs text-gray-500 uppercase">Ad Text</p>
            <p className="text-sm mt-1">{ad.ad_text}</p>
          </div>
        )}

        {ad.landing_page_url && (
          <div className="mt-4">
            <p className="text-xs text-gray-500 uppercase">Landing Page</p>
            <p className="text-sm mt-1 text-blue-600 truncate">{ad.landing_page_url}</p>
          </div>
        )}

        {ad.image_url && (
          <div className="mt-4">
            <p className="text-xs text-gray-500 uppercase mb-2">Creative Preview</p>
            <img src={ad.image_url} alt={ad.ad_name} className="max-w-sm rounded-lg border" />
          </div>
        )}
      </div>

      {ad.detail_json && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <button
            onClick={() => setShowJson(!showJson)}
            className="text-sm text-blue-600 hover:underline"
          >
            {showJson ? "Hide" : "Show"} Raw JSON
          </button>
          {showJson && (
            <pre className="mt-4 p-4 bg-gray-50 rounded text-xs overflow-auto max-h-96">
              {JSON.stringify(ad.detail_json, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
