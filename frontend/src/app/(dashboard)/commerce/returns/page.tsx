"use client";

import { useEffect, useState } from "react";
import { RotateCcw, AlertTriangle, CheckCircle } from "lucide-react";
import {
  approveReturn,
  listReturns,
  rejectReturn,
  type PaginatedResponse,
  type ReturnRequest,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { ActionMenu } from "@/components/ui/action-menu";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { toast } from "@/lib/toast-store";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_MAP: Record<string, StatusVariant> = {
  pending: "warning",
  approved: "active",
  rejected: "error",
  buyer_shipped: "syncing",
  seller_received: "syncing",
  refunded: "completed",
  closed: "paused",
};

export default function ReturnsPage() {
  const [returns, setReturns] = useState<PaginatedResponse<ReturnRequest> | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  const token = getAccessToken();

  useEffect(() => {
    loadReturns();
  }, [page]);

  function loadReturns() {
    if (!token) return;
    setLoading(true);
    listReturns(WORKSPACE_ID, token, { page })
      .then(setReturns)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleApprove(returnId: string) {
    if (!token) return;
    try {
      await approveReturn(returnId, token);
      toast.success("Return approved");
      loadReturns();
    } catch {
      toast.error("Failed to approve return");
    }
  }

  async function handleReject(returnId: string) {
    if (!token) return;
    try {
      await rejectReturn(returnId, token);
      toast.success("Return rejected");
      loadReturns();
    } catch {
      toast.error("Failed to reject return");
    }
  }

  const items = returns?.items ?? [];
  const pendingCount = items.filter((r) => r.status === "pending").length;

  const columns: Column<ReturnRequest>[] = [
    {
      key: "return_id",
      header: "Return ID",
      render: (row) => <span className="text-sm font-mono text-gray-600">{row.platform_return_id}</span>,
    },
    {
      key: "type",
      header: "Type",
      render: (row) => <span className="text-sm text-gray-900">{row.return_type.replace(/_/g, " ")}</span>,
    },
    {
      key: "status",
      header: "Status",
      render: (row) => (
        <StatusBadge
          variant={STATUS_MAP[row.status] || "draft"}
          label={row.status.replace(/_/g, " ")}
        />
      ),
    },
    {
      key: "reason",
      header: "Reason",
      className: "max-w-[200px]",
      render: (row) => <span className="text-sm text-gray-600 truncate block">{row.reason || "-"}</span>,
    },
    {
      key: "refund",
      header: "Refund",
      render: (row) => <span className="text-sm text-gray-900 tabular-nums">{row.refund_amount || "-"}</span>,
    },
    {
      key: "date",
      header: "Date",
      sortable: true,
      render: (row) => <span className="text-sm text-gray-500">{new Date(row.created_at).toLocaleDateString()}</span>,
    },
    {
      key: "actions",
      header: "",
      className: "w-12",
      render: (row) =>
        row.status === "pending" ? (
          <ActionMenu
            items={[
              { label: "Approve", onClick: () => handleApprove(row.id) },
              { label: "Reject", onClick: () => handleReject(row.id), variant: "danger" },
            ]}
          />
        ) : null,
    },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Total Returns"
            value={returns?.total ?? 0}
            icon={RotateCcw}
            iconColor="text-coral"
            loading={loading}
          />
          <MetricCard
            label="Pending Review"
            value={pendingCount}
            icon={AlertTriangle}
            iconColor="text-warning"
            loading={loading}
          />
          <MetricCard
            label="Resolved"
            value={(returns?.total ?? 0) - pendingCount}
            icon={CheckCircle}
            iconColor="text-success"
            loading={loading}
          />
        </MetricBar>
      }
      aside={
        <InsightPanel defaultOpen={false}>
          <InsightItem
            icon={<AlertTriangle className="h-4 w-4 text-warning" />}
            title="Pending returns"
            description={`${pendingCount} returns need your review. Process them within 48 hours to maintain seller rating.`}
            variant="warning"
          />
          <InsightItem
            icon={<RotateCcw className="h-4 w-4 text-info" />}
            title="Return rate"
            description="Your return rate is 2.1%, below the category average of 3.5%."
            variant="default"
          />
        </InsightPanel>
      }
    >
      <DataTable
        columns={columns}
        data={items}
        keyExtractor={(row) => row.id}
        emptyTitle="No return requests"
        emptyDescription="Return requests from buyers will appear here."
        page={returns?.page}
        totalPages={returns?.total_pages}
        onPageChange={setPage}
        loading={loading}
      />
    </PageShell>
  );
}
