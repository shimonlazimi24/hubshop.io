"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, UserPlus } from "lucide-react";
import {
  getCreatorCampaign,
  updateCreatorCampaign,
  inviteCreator,
  listInvitations,
  type CreatorCampaign,
  type CreatorInvitation,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const STATUS_COLORS: Record<string, string> = {
  DRAFT: "bg-gray-100 text-gray-800",
  ACTIVE: "bg-green-100 text-green-800",
  PAUSED: "bg-yellow-100 text-yellow-800",
  COMPLETED: "bg-blue-100 text-blue-800",
  CANCELLED: "bg-red-100 text-red-800",
  PENDING: "bg-yellow-100 text-yellow-800",
  ACCEPTED: "bg-green-100 text-green-800",
  DECLINED: "bg-red-100 text-red-800",
};

export default function CreatorCampaignDetailPage() {
  const params = useParams();
  const router = useRouter();
  const campaignId = params.id as string;
  const [campaign, setCampaign] = useState<CreatorCampaign | null>(null);
  const [invitations, setInvitations] = useState<CreatorInvitation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInvite, setShowInvite] = useState(false);
  const [creatorId, setCreatorId] = useState("");
  const [message, setMessage] = useState("");
  const [offeredAmount, setOfferedAmount] = useState("");
  const [inviting, setInviting] = useState(false);

  const token = getAccessToken();

  useEffect(() => {
    if (!token || !campaignId) return;
    Promise.all([
      getCreatorCampaign(campaignId, token),
      listInvitations(campaignId, token),
    ])
      .then(([c, inv]) => {
        setCampaign(c);
        setInvitations(inv);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [campaignId]);

  async function handleStatusChange(newStatus: string) {
    if (!token || !campaign) return;
    try {
      const updated = await updateCreatorCampaign(campaign.id, { status: newStatus }, token);
      setCampaign(updated);
    } catch (err) {
      console.error(err);
    }
  }

  async function handleInvite() {
    if (!token || !creatorId) return;
    setInviting(true);
    try {
      await inviteCreator(
        campaignId,
        {
          creator_id: creatorId,
          message: message || undefined,
          offered_amount: offeredAmount || undefined,
        },
        token
      );
      const inv = await listInvitations(campaignId, token);
      setInvitations(inv);
      setShowInvite(false);
      setCreatorId("");
      setMessage("");
      setOfferedAmount("");
    } catch (err) {
      console.error(err);
    } finally {
      setInviting(false);
    }
  }

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Loading campaign...</div>;
  }

  if (!campaign) {
    return <div className="text-center py-8 text-gray-500">Campaign not found.</div>;
  }

  return (
    <div className="max-w-4xl">
      <button
        onClick={() => router.back()}
        className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </button>

      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{campaign.name}</h2>
            {campaign.description && (
              <p className="text-sm text-gray-500 mt-1">{campaign.description}</p>
            )}
          </div>
          <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${STATUS_COLORS[campaign.status] || "bg-gray-100"}`}>
            {campaign.status}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4">
          <div>
            <p className="text-xs text-gray-500">Budget</p>
            <p className="text-sm font-medium">{campaign.budget ? `$${campaign.budget}` : "\u2014"}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Start Date</p>
            <p className="text-sm font-medium">
              {campaign.start_date ? new Date(campaign.start_date).toLocaleDateString() : "\u2014"}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">End Date</p>
            <p className="text-sm font-medium">
              {campaign.end_date ? new Date(campaign.end_date).toLocaleDateString() : "\u2014"}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Created</p>
            <p className="text-sm font-medium">{new Date(campaign.created_at).toLocaleDateString()}</p>
          </div>
        </div>

        <div className="flex gap-2 mt-4">
          {campaign.status === "DRAFT" && (
            <button
              onClick={() => handleStatusChange("ACTIVE")}
              className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Activate
            </button>
          )}
          {campaign.status === "ACTIVE" && (
            <button
              onClick={() => handleStatusChange("PAUSED")}
              className="px-3 py-1.5 text-sm bg-yellow-600 text-white rounded-md hover:bg-yellow-700"
            >
              Pause
            </button>
          )}
          {campaign.status === "PAUSED" && (
            <button
              onClick={() => handleStatusChange("ACTIVE")}
              className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Resume
            </button>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">Invitations ({invitations.length})</h3>
          <button
            onClick={() => setShowInvite(!showInvite)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-coral text-white rounded-md hover:bg-coral/90"
          >
            <UserPlus className="h-3.5 w-3.5" />
            Invite Creator
          </button>
        </div>

        {showInvite && (
          <div className="px-4 py-4 border-b border-gray-200 bg-gray-50 space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Creator ID *</label>
              <input
                type="text"
                value={creatorId}
                onChange={(e) => setCreatorId(e.target.value)}
                placeholder="Creator UUID"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Message</label>
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Optional invite message"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Offered Amount ($)</label>
                <input
                  type="text"
                  value={offeredAmount}
                  onChange={(e) => setOfferedAmount(e.target.value)}
                  placeholder="500.00"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>
            </div>
            <button
              onClick={handleInvite}
              disabled={inviting || !creatorId}
              className="px-4 py-2 bg-coral text-white rounded-md text-sm font-medium hover:bg-coral/90 disabled:opacity-50"
            >
              {inviting ? "Sending..." : "Send Invitation"}
            </button>
          </div>
        )}

        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Creator ID</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Offered</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Sent</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Responded</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {invitations.map((inv) => (
              <tr key={inv.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-900 font-mono text-xs">{inv.creator_id.slice(0, 8)}...</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${STATUS_COLORS[inv.status] || "bg-gray-100"}`}>
                    {inv.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">{inv.offered_amount ? `$${inv.offered_amount}` : "\u2014"}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(inv.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {inv.responded_at ? new Date(inv.responded_at).toLocaleDateString() : "\u2014"}
                </td>
              </tr>
            ))}
            {invitations.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">No invitations yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
