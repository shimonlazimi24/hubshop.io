"use client";

import { useEffect, useState } from "react";
import { Tag, Percent, TrendingUp } from "lucide-react";
import { listPromotions, type Promotion, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_MAP: Record<string, StatusVariant> = {
  ACTIVE: "active",
  DRAFT: "warning",
  ENDED: "paused",
  CANCELLED: "error",
};

const columns: Column<Promotion>[] = [
  {
    key: "title",
    header: "Title",
    render: (row) => <span className="text-sm font-medium text-gray-900">{row.title}</span>,
  },
  {
    key: "type",
    header: "Type",
    render: (row) => <span className="text-sm text-gray-600">{row.promotion_type}</span>,
  },
  {
    key: "discount",
    header: "Discount",
    render: (row) => (
      <span className="text-sm text-gray-600">
        {row.discount_value ? `${row.discount_value}${row.discount_type === "PERCENTAGE" ? "%" : ""}` : "-"}
      </span>
    ),
  },
  {
    key: "status",
    header: "Status",
    render: (row) => (
      <StatusBadge variant={STATUS_MAP[row.status] || "draft"} label={row.status} />
    ),
  },
  {
    key: "period",
    header: "Period",
    render: (row) => (
      <span className="text-sm text-gray-500">
        {row.start_time ? new Date(row.start_time).toLocaleDateString() : "-"}
        {row.end_time ? ` - ${new Date(row.end_time).toLocaleDateString()}` : ""}
      </span>
    ),
  },
];

export default function PromotionsPage() {
  const [data, setData] = useState<PaginatedResponse<Promotion> | null>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    listPromotions(WORKSPACE_ID, token, {
      status_filter: statusFilter || undefined,
      page,
    })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [statusFilter, page]);

  const items = data?.items ?? [];
  const activeCount = items.filter((p) => p.status === "ACTIVE").length;

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Total Promotions"
            value={data?.total ?? 0}
            icon={Tag}
            iconColor="text-coral"
            loading={loading}
          />
          <MetricCard
            label="Active"
            value={activeCount}
            icon={TrendingUp}
            iconColor="text-success"
            loading={loading}
          />
          <MetricCard
            label="Avg Discount"
            value="15%"
            icon={Percent}
            iconColor="text-purple"
            loading={loading}
          />
        </MetricBar>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search promotions..."
      >
        <FilterDropdown
          label="All Statuses"
          value={statusFilter}
          options={[
            { label: "Active", value: "ACTIVE" },
            { label: "Draft", value: "DRAFT" },
            { label: "Ended", value: "ENDED" },
          ]}
          onChange={(v) => { setStatusFilter(v); setPage(1); }}
        />
      </FilterBar>

      <DataTable
        columns={columns}
        data={items}
        keyExtractor={(row) => row.id}
        emptyTitle="No promotions found"
        emptyDescription="Create promotions in TikTok Shop to see them here."
        page={data?.page}
        totalPages={data?.total_pages}
        onPageChange={setPage}
        loading={loading}
      />
    </PageShell>
  );
}
