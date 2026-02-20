"use client";

import { useEffect, useState } from "react";
import { discoverCreators, listCreatorProfiles, saveCreator, type CreatorSummary, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const TIER_COLORS: Record<string, string> = {
  NANO: "bg-gray-100 text-gray-800",
  MICRO: "bg-blue-100 text-blue-800",
  MID: "bg-purple-100 text-purple-800",
  MACRO: "bg-orange-100 text-orange-800",
  MEGA: "bg-red-100 text-red-800",
};

type Tab = "discover" | "saved";

export default function CreatorsDiscoverPage() {
  const [tab, setTab] = useState<Tab>("discover");
  const [profiles, setProfiles] = useState<PaginatedResponse<CreatorSummary> | null>(null);
  const [discoveryResults, setDiscoveryResults] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);

  const token = getAccessToken();

  useEffect(() => {
    if (tab === "saved") loadProfiles();
    else setLoading(false);
  }, [tab, page]);

  function loadProfiles() {
    if (!token) return;
    setLoading(true);
    listCreatorProfiles(WORKSPACE_ID, token, { is_saved: tab === "saved" ? true : undefined, page })
      .then(setProfiles)
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleSearch() {
    if (!token || !query.trim()) return;
    setSearching(true);
    try {
      const result = await discoverCreators(WORKSPACE_ID, { query: query.trim() }, token);
      setDiscoveryResults(result.creators);
    } catch (err) {
      console.error(err);
    } finally {
      setSearching(false);
    }
  }

  async function handleSave(creatorId: string, isSaved: boolean) {
    if (!token) return;
    try {
      await saveCreator(creatorId, !isSaved, token);
      if (tab === "saved") loadProfiles();
    } catch (err) {
      console.error(err);
    }
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: "discover", label: "Search TTCM" },
    { key: "saved", label: "Saved Creators" },
  ];

  return (
    <div>
      <div className="flex gap-2 mb-4">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => { setTab(t.key); setPage(1); }}
            className={`px-3 py-1.5 text-sm rounded-md ${tab === t.key ? "bg-gray-900 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "discover" && (
        <div>
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Search creators by keyword..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <button
              onClick={handleSearch}
              disabled={searching}
              className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {searching ? "Searching..." : "Search"}
            </button>
          </div>

          <div className="bg-white rounded-lg border border-gray-200">
            <div className="divide-y divide-gray-200">
              {discoveryResults.map((creator, i) => (
                <div key={i} className="px-4 py-3 flex items-center gap-4 hover:bg-gray-50">
                  <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-sm font-medium">
                    {((creator.display_name as string) || "?")[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">{(creator.display_name as string) || "Unknown"}</p>
                    <p className="text-xs text-gray-500">@{(creator.username as string) || "-"}</p>
                  </div>
                  <div className="text-sm text-gray-500">
                    {((creator.follower_count as number) || 0).toLocaleString()} followers
                  </div>
                </div>
              ))}
              {!searching && discoveryResults.length === 0 && (
                <div className="px-4 py-8 text-center text-gray-500">
                  Search the TikTok Creator Marketplace to discover creators
                </div>
              )}
            </div>
          </div>
          {searching && <div className="text-center py-8 text-gray-500">Searching creators...</div>}
        </div>
      )}

      {tab === "saved" && (
        <div className="bg-white rounded-lg border border-gray-200">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 text-left">
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Creator</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Tier</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Followers</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Engagement</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {profiles?.items.map((creator) => (
                <tr key={creator.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-xs font-medium">
                        {(creator.display_name || creator.username || "?")[0]}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{creator.display_name || "Unknown"}</p>
                        <p className="text-xs text-gray-500">@{creator.username || "-"}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {creator.tier && (
                      <span className={`px-2 py-1 text-xs rounded-full ${TIER_COLORS[creator.tier] || "bg-gray-100 text-gray-800"}`}>
                        {creator.tier}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{creator.follower_count.toLocaleString()}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{creator.engagement_rate ? `${creator.engagement_rate}%` : "-"}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleSave(creator.id, creator.is_saved)}
                      className="text-sm text-red-600 hover:underline"
                    >
                      Unsave
                    </button>
                  </td>
                </tr>
              ))}
              {!loading && (!profiles || profiles.items.length === 0) && (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">No saved creators</td></tr>
              )}
            </tbody>
          </table>

          {profiles && profiles.total_pages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
              <p className="text-sm text-gray-500">Page {profiles.page} of {profiles.total_pages}</p>
              <div className="flex gap-2">
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1} className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50">Previous</button>
                <button onClick={() => setPage(p => Math.min(profiles.total_pages, p + 1))} disabled={page >= profiles.total_pages} className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50">Next</button>
              </div>
            </div>
          )}

          {loading && <div className="text-center py-8 text-gray-500">Loading creators...</div>}
        </div>
      )}
    </div>
  );
}
