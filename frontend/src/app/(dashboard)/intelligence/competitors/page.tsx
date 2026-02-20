"use client";

import { useState } from "react";
import Link from "next/link";
import { Eye, Plus, Users, Clock, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface Competitor {
  id: string;
  username: string;
  display_name: string;
  follower_count: number;
  following_count: number;
  video_count: number;
  last_synced: string;
}

const MOCK_COMPETITORS: Competitor[] = [
  {
    id: "comp-1",
    username: "competitor_brand_1",
    display_name: "Brand Alpha",
    follower_count: 2_450_000,
    following_count: 312,
    video_count: 487,
    last_synced: "2026-02-20T10:30:00Z",
  },
  {
    id: "comp-2",
    username: "rival_store",
    display_name: "Rival Store Official",
    follower_count: 1_890_000,
    following_count: 156,
    video_count: 324,
    last_synced: "2026-02-20T09:15:00Z",
  },
  {
    id: "comp-3",
    username: "topshop_tt",
    display_name: "TopShop TikTok",
    follower_count: 980_000,
    following_count: 89,
    video_count: 215,
    last_synced: "2026-02-19T22:00:00Z",
  },
  {
    id: "comp-4",
    username: "beautyco_official",
    display_name: "BeautyCo",
    follower_count: 3_120_000,
    following_count: 201,
    video_count: 612,
    last_synced: "2026-02-20T08:45:00Z",
  },
  {
    id: "comp-5",
    username: "gadgets_world",
    display_name: "Gadgets World",
    follower_count: 760_000,
    following_count: 45,
    video_count: 178,
    last_synced: "2026-02-19T18:30:00Z",
  },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export default function CompetitorsPage() {
  const [competitors] = useState<Competitor[]>(MOCK_COMPETITORS);
  const [showAdd, setShowAdd] = useState(false);
  const [newUsername, setNewUsername] = useState("");

  function handleAdd() {
    if (!newUsername.trim()) return;
    // Placeholder: would call API to add competitor
    setNewUsername("");
    setShowAdd(false);
  }

  return (
    <div className="max-w-6xl">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">
          {competitors.length} competitor{competitors.length !== 1 ? "s" : ""} tracked
        </p>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
        >
          {showAdd ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showAdd ? "Cancel" : "Add Competitor"}
        </button>
      </div>

      {showAdd && (
        <div className="rounded-xl border border-gray-100 bg-white p-5 mb-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Add Competitor</h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAdd()}
              placeholder="TikTok username (e.g. @brandname)"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <button
              onClick={handleAdd}
              disabled={!newUsername.trim()}
              className="px-4 py-2 bg-gray-900 text-white rounded-md text-sm font-medium hover:bg-gray-800 disabled:opacity-50"
            >
              Track
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Competitor</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Followers</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Videos</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Last Synced</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {competitors.map((comp) => (
              <tr key={comp.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 text-sm font-medium">
                      {comp.display_name[0]}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{comp.display_name}</p>
                      <p className="text-xs text-gray-500">@{comp.username}</p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <Users className="h-3.5 w-3.5 text-gray-400" />
                    <span className="text-sm text-gray-600">{formatNumber(comp.follower_count)}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">{comp.video_count}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <Clock className="h-3.5 w-3.5 text-gray-400" />
                    <span className="text-sm text-gray-500">
                      {new Date(comp.last_synced).toLocaleDateString()}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <Link
                    href={`/intelligence/competitors/${comp.id}`}
                    className="flex items-center gap-1 text-sm text-blue-600 hover:underline"
                  >
                    <Eye className="h-3.5 w-3.5" />
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
