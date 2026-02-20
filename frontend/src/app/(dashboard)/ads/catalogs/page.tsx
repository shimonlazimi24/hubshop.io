"use client";

import { useEffect, useState } from "react";
import { listCatalogs, syncCatalogs, type Catalog, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

export default function CatalogsPage() {
  const [data, setData] = useState<PaginatedResponse<Catalog> | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [page, setPage] = useState(1);

  const token = getAccessToken();

  useEffect(() => {
    loadCatalogs();
  }, [page]);

  function loadCatalogs() {
    if (!token) return;
    setLoading(true);
    listCatalogs(WORKSPACE_ID, token, { page })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleSync() {
    if (!token) return;
    setSyncing(true);
    try {
      await syncCatalogs(WORKSPACE_ID, token);
      loadCatalogs();
    } catch (err) {
      console.error(err);
    } finally {
      setSyncing(false);
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div />
        <button
          onClick={handleSync}
          disabled={syncing}
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {syncing ? "Syncing..." : "Sync Catalogs"}
        </button>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Catalog ID</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Products</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Updated</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data?.items.map((catalog) => (
              <tr key={catalog.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{catalog.name}</td>
                <td className="px-4 py-3 text-sm text-gray-600 font-mono">{catalog.platform_catalog_id}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{catalog.product_count.toLocaleString()}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    catalog.status === "ACTIVE" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
                  }`}>
                    {catalog.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(catalog.updated_at).toLocaleDateString()}</td>
              </tr>
            ))}
            {!loading && (!data || data.items.length === 0) && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">No catalogs found</td></tr>
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

      {loading && <div className="text-center py-8 text-gray-500">Loading catalogs...</div>}
    </div>
  );
}
