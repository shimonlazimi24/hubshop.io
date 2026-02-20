"use client";

import { useEffect, useState } from "react";
import { listConversations, listShops, type Shop } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

export default function MessagesPage() {
  const [shops, setShops] = useState<Shop[]>([]);
  const [selectedShop, setSelectedShop] = useState("");
  const [conversations, setConversations] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    listShops(WORKSPACE_ID, token)
      .then(s => {
        setShops(s);
        if (s.length > 0) setSelectedShop(s[0].id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!token || !selectedShop) return;
    setLoading(true);
    listConversations(WORKSPACE_ID, selectedShop, token)
      .then(data => setConversations(data.conversations))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedShop]);

  return (
    <div>
      <div className="flex items-center gap-4 mb-4">
        {shops.length > 1 && (
          <select
            value={selectedShop}
            onChange={(e) => setSelectedShop(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            {shops.map(s => (
              <option key={s.id} value={s.id}>{s.shop_name}</option>
            ))}
          </select>
        )}
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Buyer Conversations</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {conversations.map((conv, i) => (
            <div key={i} className="px-4 py-3 hover:bg-gray-50 cursor-pointer">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">
                  {(conv.buyer_name as string) || `Conversation ${i + 1}`}
                </span>
                <span className="text-xs text-gray-400">
                  {conv.last_message_time ? new Date(conv.last_message_time as string).toLocaleDateString() : ""}
                </span>
              </div>
              {conv.last_message ? (
                <p className="text-sm text-gray-500 mt-1 truncate">{String(conv.last_message)}</p>
              ) : null}
            </div>
          ))}
          {!loading && conversations.length === 0 && (
            <div className="px-4 py-8 text-center text-gray-500">No conversations found</div>
          )}
        </div>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Loading conversations...</div>}
    </div>
  );
}
