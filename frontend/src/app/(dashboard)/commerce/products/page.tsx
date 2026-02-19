"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  listProducts,
  listShops,
  syncProducts,
  type PaginatedResponse,
  type ProductSummary,
  type Shop,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_COLORS: Record<string, string> = {
  live: "bg-green-100 text-green-800",
  pending: "bg-yellow-100 text-yellow-800",
  draft: "bg-gray-100 text-gray-800",
  seller_deactivated: "bg-red-100 text-red-800",
  platform_deactivated: "bg-red-100 text-red-800",
  frozen: "bg-blue-100 text-blue-800",
  deleted: "bg-red-100 text-red-800",
};

export default function ProductsPage() {
  const [products, setProducts] = useState<PaginatedResponse<ProductSummary> | null>(null);
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [shopFilter, setShopFilter] = useState("");
  const [page, setPage] = useState(1);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    listShops(WORKSPACE_ID, token).then(setShops).catch(console.error);
  }, []);

  useEffect(() => {
    loadProducts();
  }, [search, statusFilter, shopFilter, page]);

  function loadProducts() {
    if (!token) return;
    setLoading(true);
    listProducts(WORKSPACE_ID, token, {
      search: search || undefined,
      status_filter: statusFilter || undefined,
      shop_id: shopFilter || undefined,
      page,
    })
      .then(setProducts)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleSync() {
    if (!token) return;
    setSyncing(true);
    try {
      const result = await syncProducts(WORKSPACE_ID, token);
      alert(`Synced ${result.synced} products`);
      loadProducts();
    } catch (err) {
      console.error(err);
    } finally {
      setSyncing(false);
    }
  }

  return (
    <div>
      {/* Filters */}
      <div className="flex items-center gap-4 mb-4">
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm w-64"
        />
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm"
        >
          <option value="">All Statuses</option>
          <option value="live">Live</option>
          <option value="pending">Pending</option>
          <option value="draft">Draft</option>
          <option value="seller_deactivated">Seller Deactivated</option>
        </select>
        {shops.length > 1 && (
          <select
            value={shopFilter}
            onChange={(e) => {
              setShopFilter(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">All Shops</option>
            {shops.map((s) => (
              <option key={s.id} value={s.id}>
                {s.shop_name}
              </option>
            ))}
          </select>
        )}
        <div className="flex-1" />
        <button
          onClick={handleSync}
          disabled={syncing}
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {syncing ? "Syncing..." : "Sync Products"}
        </button>
      </div>

      {/* Products table */}
      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Product</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Price</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Inventory</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">SKUs</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Updated</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {products?.items.map((product) => (
              <tr key={product.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    {product.main_image_url && (
                      <img
                        src={product.main_image_url}
                        alt=""
                        className="w-10 h-10 rounded object-cover"
                      />
                    )}
                    <Link
                      href={`/commerce/products/${product.id}`}
                      className="text-sm font-medium text-blue-600 hover:underline line-clamp-1"
                    >
                      {product.title}
                    </Link>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      STATUS_COLORS[product.status] || "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {product.status.replace(/_/g, " ")}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-900">
                  {product.price_amount
                    ? `${product.currency || "$"} ${product.price_amount}`
                    : "-"}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {product.inventory_total}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {product.sku_count}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {new Date(product.updated_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
            {!loading && products?.items.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  No products found
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {products && products.total_pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Page {products.page} of {products.total_pages} ({products.total} total)
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => Math.min(products.total_pages, p + 1))}
                disabled={page >= products.total_pages}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Loading products...</div>}
    </div>
  );
}
