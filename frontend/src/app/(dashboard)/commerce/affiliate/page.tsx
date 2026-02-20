"use client";

import { useEffect, useState } from "react";
import {
  listAffiliateProducts,
  listCollaborations,
  type AffiliateProduct,
  type OpenCollaboration,
  type PaginatedResponse,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

export default function AffiliatePage() {
  const [products, setProducts] = useState<PaginatedResponse<AffiliateProduct> | null>(null);
  const [collabs, setCollabs] = useState<PaginatedResponse<OpenCollaboration> | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    Promise.all([
      listAffiliateProducts(WORKSPACE_ID, token, { page }),
      listCollaborations(WORKSPACE_ID, token),
    ])
      .then(([p, c]) => { setProducts(p); setCollabs(c); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [page]);

  return (
    <div>
      <div className="bg-white rounded-lg border border-gray-200 mb-6">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Affiliate Products</h3>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Product</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Commission</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Added</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {products?.items.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-900">{p.product_id}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{p.commission_rate || "-"}%</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${p.status === "ACTIVE" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}`}>
                    {p.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(p.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
            {!loading && (!products || products.items.length === 0) && (
              <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">No affiliate products yet</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Collaborations</h3>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Product</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Commission</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {collabs?.items.map((c) => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-900">{c.product_id}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{c.commission_rate}%</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">{c.status}</span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(c.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
            {!loading && (!collabs || collabs.items.length === 0) && (
              <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">No collaborations yet</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Loading...</div>}
    </div>
  );
}
