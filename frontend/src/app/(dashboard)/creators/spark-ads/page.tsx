"use client";

import { useEffect, useState } from "react";
import { listSparkAds, requestSparkAdAuthorization, type ContentAuthorization } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_COLORS: Record<string, string> = {
  PENDING: "bg-yellow-100 text-yellow-800",
  APPROVED: "bg-green-100 text-green-800",
  EXPIRED: "bg-gray-100 text-gray-800",
  REJECTED: "bg-red-100 text-red-800",
};

export default function SparkAdsPage() {
  const [authorizations, setAuthorizations] = useState<ContentAuthorization[]>([]);
  const [loading, setLoading] = useState(true);
  const [showRequest, setShowRequest] = useState(false);
  const [requesting, setRequesting] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");

  const [formCreatorId, setFormCreatorId] = useState("");
  const [formVideoId, setFormVideoId] = useState("");

  const token = getAccessToken();

  useEffect(() => {
    loadAuthorizations();
  }, [statusFilter]);

  function loadAuthorizations() {
    if (!token) return;
    setLoading(true);
    listSparkAds(WORKSPACE_ID, token, {
      status_filter: statusFilter || undefined,
    })
      .then(setAuthorizations)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleRequest() {
    if (!token || !formCreatorId.trim() || !formVideoId.trim()) return;
    setRequesting(true);
    try {
      await requestSparkAdAuthorization(WORKSPACE_ID, {
        creator_id: formCreatorId.trim(),
        platform_video_id: formVideoId.trim(),
      }, token);
      setShowRequest(false);
      setFormCreatorId("");
      setFormVideoId("");
      loadAuthorizations();
    } catch (err) {
      console.error(err);
    } finally {
      setRequesting(false);
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm"
        >
          <option value="">All Statuses</option>
          <option value="PENDING">Pending</option>
          <option value="APPROVED">Approved</option>
          <option value="EXPIRED">Expired</option>
        </select>
        <button
          onClick={() => setShowRequest(!showRequest)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
        >
          {showRequest ? "Cancel" : "Request Authorization"}
        </button>
      </div>

      {showRequest && (
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Request Spark Ad Authorization</h3>
          <div className="space-y-3">
            <input
              type="text"
              value={formCreatorId}
              onChange={(e) => setFormCreatorId(e.target.value)}
              placeholder="Creator ID"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <input
              type="text"
              value={formVideoId}
              onChange={(e) => setFormVideoId(e.target.value)}
              placeholder="TikTok Video ID"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <button
              onClick={handleRequest}
              disabled={requesting || !formCreatorId.trim() || !formVideoId.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {requesting ? "Requesting..." : "Submit Request"}
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Creator</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Video ID</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Auth Code</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Expires</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {authorizations.map((auth) => (
              <tr key={auth.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-900 font-mono">{auth.creator_id}</td>
                <td className="px-4 py-3 text-sm text-gray-600 font-mono">{auth.platform_video_id || "-"}</td>
                <td className="px-4 py-3 text-sm text-gray-600 font-mono">
                  {auth.authorization_code ? (
                    <span className="bg-gray-50 px-2 py-1 rounded text-xs">{auth.authorization_code}</span>
                  ) : "-"}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${STATUS_COLORS[auth.status] || "bg-gray-100 text-gray-800"}`}>
                    {auth.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {auth.expires_at ? new Date(auth.expires_at).toLocaleDateString() : "-"}
                </td>
              </tr>
            ))}
            {!loading && authorizations.length === 0 && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">No Spark Ad authorizations</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Loading authorizations...</div>}
    </div>
  );
}
