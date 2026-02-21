"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowLeft, Package, DollarSign, Layers } from "lucide-react";
import { getProduct, type ProductDetail } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { DataTable, type Column } from "@/components/ui/data-table";

interface Sku {
  id: string;
  platform_sku_id: string;
  sku_name: string | null;
  seller_sku: string | null;
  price_amount: string | null;
  inventory_quantity: number;
}

const skuColumns: Column<Sku>[] = [
  {
    key: "sku_id",
    header: "SKU ID",
    render: (row) => <span className="text-sm text-gray-600 font-mono">{row.platform_sku_id}</span>,
  },
  {
    key: "name",
    header: "Name",
    render: (row) => <span className="text-sm text-gray-900">{row.sku_name || "-"}</span>,
  },
  {
    key: "seller_sku",
    header: "Seller SKU",
    render: (row) => <span className="text-sm text-gray-600">{row.seller_sku || "-"}</span>,
  },
  {
    key: "price",
    header: "Price",
    render: (row) => <span className="text-sm text-gray-900 tabular-nums">{row.price_amount || "-"}</span>,
  },
  {
    key: "inventory",
    header: "Inventory",
    sortable: true,
    render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.inventory_quantity}</span>,
  },
];

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [showRawJson, setShowRawJson] = useState(false);

  useEffect(() => {
    const token = getAccessToken();
    if (!token || !params.id) return;

    getProduct(params.id as string, token)
      .then(setProduct)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [params.id]);

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Loading product...</div>;
  }

  if (!product) {
    return <div className="text-center py-8 text-gray-500">Product not found</div>;
  }

  return (
    <div>
      <button
        onClick={() => router.back()}
        className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" /> Back to products
      </button>

      <PageShell
        header={
          <MetricBar>
            <MetricCard
              label="Price"
              value={product.price_amount ? `${product.currency || "$"}${product.price_amount}` : "-"}
              icon={DollarSign}
              iconColor="text-success"
            />
            <MetricCard
              label="Inventory"
              value={product.inventory_total}
              icon={Package}
              iconColor="text-coral"
            />
            <MetricCard
              label="SKUs"
              value={product.skus.length}
              icon={Layers}
              iconColor="text-purple"
            />
          </MetricBar>
        }
      >
        {/* Product header */}
        <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-[var(--shadow-card)] mb-6">
          <div className="flex items-start gap-6">
            {product.main_image_url && (
              <img
                src={product.main_image_url}
                alt=""
                className="w-24 h-24 rounded-xl object-cover shadow-sm"
              />
            )}
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">{product.title}</h3>
              <p className="text-sm text-gray-500 mt-1">ID: {product.platform_product_id}</p>
              <div className="flex items-center gap-3 mt-3">
                <StatusBadge
                  variant={product.status === "live" ? "active" : product.status === "pending" ? "warning" : "draft"}
                  label={product.status.replace(/_/g, " ")}
                />
                <span className="text-sm text-gray-500">
                  {product.inventory_total} in stock
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* SKUs Table */}
        <h3 className="text-sm font-semibold text-gray-900 mb-3">SKUs ({product.skus.length})</h3>
        <DataTable
          columns={skuColumns}
          data={product.skus}
          keyExtractor={(row) => row.id}
          emptyTitle="No SKUs"
          className="mb-6"
        />

        {/* Raw JSON */}
        {product.detail_json && (
          <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] overflow-hidden">
            <button
              onClick={() => setShowRawJson(!showRawJson)}
              className="w-full px-5 py-4 text-left text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              {showRawJson ? "Hide" : "Show"} Raw API Response
            </button>
            {showRawJson && (
              <pre className="px-5 py-4 border-t border-gray-100 overflow-auto text-xs text-gray-600 max-h-96 bg-gray-50/50">
                {JSON.stringify(product.detail_json, null, 2)}
              </pre>
            )}
          </div>
        )}
      </PageShell>
    </div>
  );
}
