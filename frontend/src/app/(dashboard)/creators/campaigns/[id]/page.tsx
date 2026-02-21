"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, UserPlus, DollarSign, Calendar, Clock, Users } from "lucide-react";
import {
  getCreatorCampaign,
  updateCreatorCampaign,
  inviteCreator,
  listInvitations,
  type CreatorCampaign,
  type CreatorInvitation,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { Modal } from "@/components/ui/modal";

const STATUS_MAP: Record<string, StatusVariant> = {
  DRAFT: "draft",
  ACTIVE: "active",
  PAUSED: "paused",
  COMPLETED: "completed",
  CANCELLED: "error",
  PENDING: "warning",
  ACCEPTED: "active",
  DECLINED: "error",
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
      .catch(() => toast.error("Failed to load campaign"))
      .finally(() => setLoading(false));
  }, [campaignId]);

  async function handleStatusChange(newStatus: string) {
    if (!token || !campaign) return;
    try {
      const updated = await updateCreatorCampaign(campaign.id, { status: newStatus }, token);
      setCampaign(updated);
      toast.success(`Campaign ${newStatus.toLowerCase()}`);
    } catch {
      toast.error("Failed to update campaign status");
    }
  }

  async function handleInvite() {
    if (!token || !creatorId) return;
    setInviting(true);
    try {
      await inviteCreator(campaignId, {
        creator_id: creatorId,
        message: message || undefined,
        offered_amount: offeredAmount || undefined,
      }, token);
      const inv = await listInvitations(campaignId, token);
      setInvitations(inv);
      setShowInvite(false);
      setCreatorId("");
      setMessage("");
      setOfferedAmount("");
      toast.success("Invitation sent successfully");
    } catch {
      toast.error("Failed to send invitation");
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

  const acceptedCount = invitations.filter((i) => i.status === "ACCEPTED").length;
  const pendingCount = invitations.filter((i) => i.status === "PENDING").length;

  const columns: Column<CreatorInvitation>[] = [
    {
      key: "creator",
      header: "Creator ID",
      render: (row) => <span className="text-sm font-mono">{row.creator_id.slice(0, 8)}...</span>,
    },
    {
      key: "status",
      header: "Status",
      render: (row) => <StatusBadge variant={STATUS_MAP[row.status] || "draft"} label={row.status} />,
    },
    {
      key: "offered",
      header: "Offered",
      render: (row) => <span className="text-sm">{row.offered_amount ? `$${row.offered_amount}` : "\u2014"}</span>,
    },
    {
      key: "sent",
      header: "Sent",
      render: (row) => <span className="text-sm text-gray-500">{new Date(row.created_at).toLocaleDateString()}</span>,
    },
    {
      key: "responded",
      header: "Responded",
      render: (row) => <span className="text-sm text-gray-500">{row.responded_at ? new Date(row.responded_at).toLocaleDateString() : "\u2014"}</span>,
    },
  ];

  return (
    <PageShell
      header={
        <>
          <button onClick={() => router.back()} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-4">
            <ArrowLeft className="h-4 w-4" /> Back
          </button>
          <div className="bg-white rounded-xl border border-gray-100 p-6 shadow-[var(--shadow-card)] mb-6">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">{campaign.name}</h2>
                {campaign.description && <p className="text-sm text-gray-500 mt-1">{campaign.description}</p>}
              </div>
              <StatusBadge variant={STATUS_MAP[campaign.status] || "draft"} label={campaign.status} />
            </div>
            <div className="flex gap-2 mt-4">
              {campaign.status === "DRAFT" && (
                <button onClick={() => handleStatusChange("ACTIVE")} className="px-3 py-1.5 text-sm bg-success text-white rounded-lg hover:bg-success/90">Activate</button>
              )}
              {campaign.status === "ACTIVE" && (
                <button onClick={() => handleStatusChange("PAUSED")} className="px-3 py-1.5 text-sm bg-warning text-white rounded-lg hover:bg-warning/90">Pause</button>
              )}
              {campaign.status === "PAUSED" && (
                <button onClick={() => handleStatusChange("ACTIVE")} className="px-3 py-1.5 text-sm bg-success text-white rounded-lg hover:bg-success/90">Resume</button>
              )}
            </div>
          </div>
          <MetricBar>
            <MetricCard label="Budget" value={campaign.budget ? `$${campaign.budget}` : "\u2014"} icon={DollarSign} />
            <MetricCard label="Invitations" value={invitations.length} icon={Users} />
            <MetricCard label="Accepted" value={acceptedCount} icon={Users} trend={{ value: acceptedCount > 0 ? Math.round((acceptedCount / invitations.length) * 100) : 0, direction: "flat", label: "% rate" }} />
            <MetricCard label="Pending" value={pendingCount} icon={Clock} />
          </MetricBar>
        </>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Acceptance rate" description={`${invitations.length > 0 ? Math.round((acceptedCount / invitations.length) * 100) : 0}% of invited creators accepted.`} variant={acceptedCount > 0 ? "success" : "default"} />
          <InsightItem title="Tip" description="Personalized messages increase acceptance rates by 35%." />
        </InsightPanel>
      }
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Invitations ({invitations.length})</h3>
        <button onClick={() => setShowInvite(true)} className="flex items-center gap-1.5 px-3 py-2 text-sm bg-coral text-white rounded-lg hover:bg-coral/90 font-medium transition-colors">
          <UserPlus className="h-3.5 w-3.5" /> Invite Creator
        </button>
      </div>

      <DataTable
        columns={columns}
        data={invitations}
        keyExtractor={(row) => row.id}
        emptyTitle="No invitations yet"
        emptyDescription="Invite creators to join this campaign"
        emptyAction={{ label: "Invite Creator", onClick: () => setShowInvite(true) }}
      />

      <Modal open={showInvite} onClose={() => setShowInvite(false)} title="Invite Creator">
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Creator ID *</label>
            <input type="text" value={creatorId} onChange={(e) => setCreatorId(e.target.value)} placeholder="Creator UUID" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Message</label>
              <input type="text" value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Optional invite message" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Offered Amount ($)</label>
              <input type="text" value={offeredAmount} onChange={(e) => setOfferedAmount(e.target.value)} placeholder="500.00" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button onClick={() => setShowInvite(false)} className="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50">Cancel</button>
            <button onClick={handleInvite} disabled={inviting || !creatorId} className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 disabled:opacity-50">{inviting ? "Sending..." : "Send Invitation"}</button>
          </div>
        </div>
      </Modal>
    </PageShell>
  );
}
