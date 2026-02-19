"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getProduct, type ProductDetail } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

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
        className="text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        &larr; Back to products
      </button>

      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-start gap-6">
          {product.main_image_url && (
            <img
              src={product.main_image_url}
              alt=""
              className="w-24 h-24 rounded-lg object-cover"
            />
          )}
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-gray-900">{product.title}</h3>
            <p className="text-sm text-gray-500 mt-1">
              ID: {product.platform_product_id}
            </p>
            <div className="flex items-center gap-4 mt-3">
              <span
                className={`px-2 py-1 text-xs rounded-full ${
                  product.status === "live"
                    ? "bg-green-100 text-green-800"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {product.status.replace(/_/g, " ")}
              </span>
              {product.price_amount && (
                <span className="text-sm font-medium text-gray-900">
                  {product.currency || "$"} {product.price_amount}
                </span>
              )}
              <span className="text-sm text-gray-500">
                {product.inventory_total} in stock
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* SKUs */}
      <div className="bg-white rounded-lg border border-gray-200 mb-6">
        <div className="p-4 border-b border-gray-200">
          <h3 className="font-semibold text-gray-900">
            SKUs ({product.skus.length})
          </h3>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">SKU ID</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Seller SKU</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Price</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Inventory</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {product.skus.map((sku) => (
              <tr key={sku.id}>
                <td className="px-4 py-3 text-sm text-gray-600 font-mono">
                  {sku.platform_sku_id}
                </td>
                <td className="px-4 py-3 text-sm text-gray-900">
                  {sku.sku_name || "-"}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {sku.seller_sku || "-"}
                </td>
                <td className="px-4 py-3 text-sm text-gray-900">
                  {sku.price_amount || "-"}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {sku.inventory_quantity}
                </td>
              </tr>
            ))}
            {product.skus.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-gray-500">
                  No SKUs
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Raw JSON */}
      {product.detail_json && (
        <div className="bg-white rounded-lg border border-gray-200">
          <button
            onClick={() => setShowRawJson(!showRawJson)}
            className="w-full p-4 text-left text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            {showRawJson ? "Hide" : "Show"} Raw API Response
          </button>
          {showRawJson && (
            <pre className="p-4 border-t border-gray-200 overflow-auto text-xs text-gray-600 max-h-96">
              {JSON.stringify(product.detail_json, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
