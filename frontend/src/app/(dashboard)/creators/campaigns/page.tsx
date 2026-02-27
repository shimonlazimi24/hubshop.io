"use client";

import { useEffect, useState } from "react";
import { Briefcase, DollarSign, Users, Target } from "lucide-react";
import { listCreatorCampaigns, createCreatorCampaign, listInvitations, type CreatorCampaign, type CreatorInvitation, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { Modal } from "@/components/ui/modal";
import { ActionMenu } from "@/components/ui/action-menu";
import { useWorkspace } from "@/hooks/useWorkspace";


const STATUS_MAP: Record<string, StatusVariant> = {
  DRAFT: "draft",
  ACTIVE: "active",
  PAUSED: "paused",
  COMPLETED: "completed",
  CANCELLED: "error",
};

export default function CreatorCampaignsPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const [data, setData] = useState<PaginatedResponse<CreatorCampaign> | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
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
    if (!token || !WORKSPACE_ID) return;
    setLoading(true);
    listCreatorCampaigns(WORKSPACE_ID, token, {
      status_filter: statusFilter || undefined,
      page,
    })
      .then(setData)
      .catch(() => toast.error("Failed to load campaigns"))
      .finally(() => setLoading(false));
  }

  async function handleCreate() {
    if (!token || !WORKSPACE_ID || !formName.trim()) return;
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
      toast.success("Campaign created successfully");
      loadCampaigns();
    } catch {
      toast.error("Failed to create campaign");
    } finally {
      setCreating(false);
    }
  }

  async function handleViewInvitations(campaignId: string) {
    if (!token || !WORKSPACE_ID) return;
    setSelectedCampaign(campaignId);
    try {
      const result = await listInvitations(campaignId, token);
      setInvitations(result);
    } catch {
      toast.error("Failed to load invitations");
    }
  }

  const activeCampaigns = data?.items.filter((c) => c.status === "ACTIVE").length ?? 0;
  const totalBudget = data?.items.reduce((sum, c) => sum + (parseFloat(c.budget || "0") || 0), 0) ?? 0;

  const columns: Column<CreatorCampaign>[] = [
    {
      key: "name",
      header: "Campaign",
      render: (row) => (
        <div>
          <p className="text-sm font-medium text-gray-900">{row.name}</p>
          {row.description && <p className="text-xs text-gray-500 mt-0.5 truncate max-w-xs">{row.description}</p>}
        </div>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (row) => <StatusBadge variant={STATUS_MAP[row.status] || "draft"} label={row.status} />,
    },
    {
      key: "budget",
      header: "Budget",
      sortable: true,
      render: (row) => <span className="text-sm tabular-nums">{row.budget ? `$${row.budget}` : "-"}</span>,
    },
    {
      key: "period",
      header: "Period",
      render: (row) => (
        <span className="text-sm text-gray-500">
          {row.start_date ? new Date(row.start_date).toLocaleDateString() : "-"}
          {row.end_date ? ` - ${new Date(row.end_date).toLocaleDateString()}` : ""}
        </span>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      className: "w-24",
      render: (row) => (
        <ActionMenu items={[
          { label: "View Invitations", onClick: () => handleViewInvitations(row.id) },
          { label: "Edit", onClick: () => {} },
        ]} />
      ),
    },
  ];

  const invitationColumns: Column<CreatorInvitation>[] = [
    {
      key: "creator",
      header: "Creator ID",
      render: (row) => <span className="text-sm font-mono text-gray-900">{row.creator_id}</span>,
    },
    {
      key: "status",
      header: "Status",
      render: (row) => {
        const variant: StatusVariant = row.status === "ACCEPTED" ? "active" : row.status === "REJECTED" ? "error" : "warning";
        return <StatusBadge variant={variant} label={row.status} />;
      },
    },
    {
      key: "offered",
      header: "Offered",
      render: (row) => <span className="text-sm">{row.offered_amount || "-"}</span>,
    },
    {
      key: "sent",
      header: "Sent",
      render: (row) => <span className="text-sm text-gray-500">{new Date(row.created_at).toLocaleDateString()}</span>,
    },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Total Campaigns" value={data?.total ?? 0} icon={Briefcase} trend={{ value: 2, direction: "up", label: "this month" }} />
          <MetricCard label="Active" value={activeCampaigns} icon={Target} />
          <MetricCard label="Total Budget" value={`$${totalBudget.toLocaleString()}`} icon={DollarSign} />
          <MetricCard label="Creators Invited" value={12} icon={Users} trend={{ value: 5, direction: "up" }} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Budget optimization" description="2 campaigns using less than 30% of budget. Consider reallocating." variant="warning" />
          <InsightItem title="High-performing campaign" description="Summer Launch has 92% creator acceptance rate." variant="success" />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search campaigns..."
        actions={
          <button
            onClick={() => setShowCreate(true)}
            className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 transition-colors"
          >
            New Campaign
          </button>
        }
      >
        <FilterDropdown
          label="Status"
          value={statusFilter}
          onChange={(v) => { setStatusFilter(v); setPage(1); }}
          options={[
            { label: "Draft", value: "DRAFT" },
            { label: "Active", value: "ACTIVE" },
            { label: "Paused", value: "PAUSED" },
            { label: "Completed", value: "COMPLETED" },
          ]}
        />
      </FilterBar>

      <DataTable
        columns={columns}
        data={(data?.items ?? []).filter((c) => !search || c.name.toLowerCase().includes(search.toLowerCase()))}
        keyExtractor={(row) => row.id}
        loading={loading}
        page={page}
        totalPages={data?.total_pages ?? 1}
        onPageChange={setPage}
        emptyTitle="No campaigns found"
        emptyDescription="Create your first creator campaign to get started"
        emptyAction={{ label: "New Campaign", onClick: () => setShowCreate(true) }}
      />

      {/* Create Campaign Modal */}
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Create Campaign">
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Campaign Name *</label>
            <input type="text" value={formName} onChange={(e) => setFormName(e.target.value)} placeholder="Campaign name" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
            <textarea value={formDescription} onChange={(e) => setFormDescription(e.target.value)} placeholder="Description (optional)" rows={2} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Budget ($)</label>
            <input type="text" value={formBudget} onChange={(e) => setFormBudget(e.target.value)} placeholder="Budget (optional)" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button onClick={() => setShowCreate(false)} className="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50">Cancel</button>
            <button onClick={handleCreate} disabled={creating || !formName.trim()} className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 disabled:opacity-50">{creating ? "Creating..." : "Create"}</button>
          </div>
        </div>
      </Modal>

      {/* Invitations Modal */}
      <Modal open={!!selectedCampaign} onClose={() => setSelectedCampaign(null)} title="Invitations" size="lg">
        <DataTable
          columns={invitationColumns}
          data={invitations}
          keyExtractor={(row) => row.id}
          emptyTitle="No invitations"
          emptyDescription="Invite creators from the campaign detail page"
        />
      </Modal>
    </PageShell>
  );
}
