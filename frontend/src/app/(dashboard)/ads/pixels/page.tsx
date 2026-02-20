"use client";

import { useEffect, useState } from "react";
import { listPixels, getPixelCode, type Pixel, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

export default function PixelsPage() {
  const [data, setData] = useState<PaginatedResponse<Pixel> | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPixel, setSelectedPixel] = useState<string | null>(null);
  const [pixelCode, setPixelCode] = useState<string | null>(null);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    listPixels(WORKSPACE_ID, token)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  async function handleGetCode(pixelId: string) {
    if (!token) return;
    setSelectedPixel(pixelId);
    try {
      const result = await getPixelCode(pixelId, token);
      setPixelCode(result.pixel_code);
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div>
      <div className="bg-white rounded-lg border border-gray-200 mb-6">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Pixel ID</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Created</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data?.items.map((pixel) => (
              <tr key={pixel.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{pixel.name}</td>
                <td className="px-4 py-3 text-sm text-gray-600 font-mono">{pixel.platform_pixel_id}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(pixel.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleGetCode(pixel.id)}
                    className="text-sm text-blue-600 hover:underline"
                  >
                    Get Code
                  </button>
                </td>
              </tr>
            ))}
            {!loading && (!data || data.items.length === 0) && (
              <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">No pixels found</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {selectedPixel && pixelCode && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Pixel Code</h3>
          <pre className="bg-gray-50 rounded p-3 text-xs overflow-x-auto">
            <code>{pixelCode}</code>
          </pre>
        </div>
      )}

      {loading && <div className="text-center py-8 text-gray-500">Loading pixels...</div>}
    </div>
  );
}
