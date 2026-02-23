"use client";

import { useEffect, useState } from "react";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
import { Users, Percent, TrendingUp } from "lucide-react";
import {
  listAffiliateProducts,
  listCollaborations,
  type AffiliateProduct,
  type OpenCollaboration,
  type PaginatedResponse,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const affiliateColumns: Column<AffiliateProduct>[] = [
  {
    key: "product",
    header: "Product",
    render: (row) => <span className="text-sm text-gray-900">{row.product_id}</span>,
  },
  {
    key: "commission",
    header: "Commission",
    sortable: true,
    render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.commission_rate || "-"}%</span>,
  },
  {
    key: "status",
    header: "Status",
    render: (row) => (
      <StatusBadge
        variant={row.status === "ACTIVE" ? "active" : "paused"}
        label={row.status}
      />
    ),
  },
  {
    key: "added",
    header: "Added",
    sortable: true,
    render: (row) => <span className="text-sm text-gray-500">{new Date(row.created_at).toLocaleDateString()}</span>,
  },
];

const collabColumns: Column<OpenCollaboration>[] = [
  {
    key: "product",
    header: "Product",
    render: (row) => <span className="text-sm text-gray-900">{row.product_id}</span>,
  },
  {
    key: "commission",
    header: "Commission",
    sortable: true,
    render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.commission_rate}%</span>,
  },
  {
    key: "status",
    header: "Status",
    render: (row) => <StatusBadge variant="syncing" label={row.status} />,
  },
  {
    key: "created",
    header: "Created",
    sortable: true,
    render: (row) => <span className="text-sm text-gray-500">{new Date(row.created_at).toLocaleDateString()}</span>,
  },
];

export default function AffiliatePage() {
  const [products, setProducts] = useState<PaginatedResponse<AffiliateProduct> | null>(null);
  const [collabs, setCollabs] = useState<PaginatedResponse<OpenCollaboration> | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  const { platform } = usePlatformFilter();
  const platformParam = platform === "all" ? undefined : platform;
  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    Promise.all([
      listAffiliateProducts(WORKSPACE_ID, token, { platform: platformParam, page }),
      listCollaborations(WORKSPACE_ID, token, { platform: platformParam }),
    ])
      .then(([p, c]) => { setProducts(p); setCollabs(c); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [platform, page]);

  const activeProducts = products?.items.filter((p) => p.status === "ACTIVE").length ?? 0;

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Affiliate Products"
            value={products?.total ?? 0}
            icon={Users}
            iconColor="text-coral"
            loading={loading}
          />
          <MetricCard
            label="Active"
            value={activeProducts}
            icon={TrendingUp}
            iconColor="text-success"
            loading={loading}
          />
          <MetricCard
            label="Collaborations"
            value={collabs?.total ?? 0}
            icon={Percent}
            iconColor="text-purple"
            loading={loading}
          />
        </MetricBar>
      }
    >
      {/* Affiliate Products */}
      <h3 className="text-sm font-semibold text-gray-900 mb-3">Affiliate Products</h3>
      <DataTable
        columns={affiliateColumns}
        data={products?.items ?? []}
        keyExtractor={(row) => row.id}
        emptyTitle="No affiliate products yet"
        emptyDescription="Add products to the affiliate program in TikTok Shop."
        className="mb-6"
        loading={loading}
      />

      {/* Collaborations */}
      <h3 className="text-sm font-semibold text-gray-900 mb-3">Collaborations</h3>
      <DataTable
        columns={collabColumns}
        data={collabs?.items ?? []}
        keyExtractor={(row) => row.id}
        emptyTitle="No collaborations yet"
        emptyDescription="Open collaborations will appear here."
        loading={loading}
      />
    </PageShell>
  );
}
