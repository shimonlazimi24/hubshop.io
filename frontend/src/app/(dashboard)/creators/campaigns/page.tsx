"use client";

import { useEffect, useState } from "react";
import { listCreatorCampaigns, createCreatorCampaign, listInvitations, type CreatorCampaign, type CreatorInvitation, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_COLORS: Record<string, string> = {
  DRAFT: "bg-yellow-100 text-yellow-800",
  ACTIVE: "bg-green-100 text-green-800",
  PAUSED: "bg-gray-100 text-gray-800",
  COMPLETED: "bg-blue-100 text-blue-800",
  CANCELLED: "bg-red-100 text-red-800",
};

export default function CreatorCampaignsPage() {
  const [data, setData] = useState<PaginatedResponse<CreatorCampaign> | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [selectedCampaign, setSelectedCampaign] = useState<string | null>(null);
  const [invitations, setInvitations] = useState<CreatorInvitation[]>([]);

  const [formName, setFormName] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [formBudget, setFormBudget] = useState("");

  const token = getAccessToken();

  useEffect(() => {
    loadCampaigns();
  }, [statusFilter, page]);

  function loadCampaigns() {
    if (!token) return;
    setLoading(true);
    listCreatorCampaigns(WORKSPACE_ID, token, {
      status_filter: statusFilter || undefined,
      page,
    })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleCreate() {
    if (!token || !formName.trim()) return;
    setCreating(true);
    try {
      await createCreatorCampaign(WORKSPACE_ID, {
        name: formName.trim(),
        description: formDescription || undefined,
        budget: formBudget || undefined,
      }, token);
      setShowCreate(false);
      setFormName("");
      setFormDescription("");
      setFormBudget("");
      loadCampaigns();
    } catch (err) {
      console.error(err);
    } finally {
      setCreating(false);
    }
  }

  async function handleViewInvitations(campaignId: string) {
    if (!token) return;
    setSelectedCampaign(campaignId);
    try {
      const result = await listInvitations(campaignId, token);
      setInvitations(result);
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm"
        >
          <option value="">All Statuses</option>
          <option value="DRAFT">Draft</option>
          <option value="ACTIVE">Active</option>
          <option value="PAUSED">Paused</option>
          <option value="COMPLETED">Completed</option>
        </select>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
        >
          {showCreate ? "Cancel" : "New Campaign"}
        </button>
      </div>

      {showCreate && (
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Create Campaign</h3>
          <div className="space-y-3">
            <input
              type="text"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder="Campaign name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <textarea
              value={formDescription}
              onChange={(e) => setFormDescription(e.target.value)}
              placeholder="Description (optional)"
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <input
              type="text"
              value={formBudget}
              onChange={(e) => setFormBudget(e.target.value)}
              placeholder="Budget (optional)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <button
              onClick={handleCreate}
              disabled={creating || !formName.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {creating ? "Creating..." : "Create"}
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Budget</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Period</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data?.items.map((campaign) => (
              <tr key={campaign.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <p className="text-sm font-medium text-gray-900">{campaign.name}</p>
                  {campaign.description && <p className="text-xs text-gray-500 mt-1 truncate max-w-xs">{campaign.description}</p>}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${STATUS_COLORS[campaign.status] || "bg-gray-100 text-gray-800"}`}>
                    {campaign.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">{campaign.budget || "-"}</td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {campaign.start_date ? new Date(campaign.start_date).toLocaleDateString() : "-"}
                  {campaign.end_date ? ` - ${new Date(campaign.end_date).toLocaleDateString()}` : ""}
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleViewInvitations(campaign.id)}
                    className="text-sm text-blue-600 hover:underline"
                  >
                    Invitations
                  </button>
                </td>
              </tr>
            ))}
            {!loading && (!data || data.items.length === 0) && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">No campaigns found</td></tr>
            )}
          </tbody>
        </table>

        {data && data.total_pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
            <p className="text-sm text-gray-500">Page {data.page} of {data.total_pages}</p>
            <div className="flex gap-2">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1} className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50">Previous</button>
              <button onClick={() => setPage(p => Math.min(data.total_pages, p + 1))} disabled={page >= data.total_pages} className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50">Next</button>
            </div>
          </div>
        )}
      </div>

      {selectedCampaign && (
        <div className="bg-white rounded-lg border border-gray-200 mt-4">
          <div className="px-4 py-3 border-b border-gray-200">
            <h3 className="text-sm font-medium text-gray-900">Invitations</h3>
          </div>
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 text-left">
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Creator ID</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Offered</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Sent</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {invitations.map((inv) => (
                <tr key={inv.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900 font-mono">{inv.creator_id}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      inv.status === "ACCEPTED" ? "bg-green-100 text-green-800" :
                      inv.status === "REJECTED" ? "bg-red-100 text-red-800" :
                      "bg-yellow-100 text-yellow-800"
                    }`}>
                      {inv.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{inv.offered_amount || "-"}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{new Date(inv.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
              {invitations.length === 0 && (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">No invitations</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {loading && <div className="text-center py-8 text-gray-500">Loading campaigns...</div>}
    </div>
  );
}
