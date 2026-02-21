"use client";

import { useState } from "react";
import Link from "next/link";
import { Eye, Users, Clock, Film } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { Modal } from "@/components/ui/modal";
import { toast } from "@/lib/toast-store";

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
  { id: "comp-1", username: "competitor_brand_1", display_name: "Brand Alpha", follower_count: 2_450_000, following_count: 312, video_count: 487, last_synced: "2026-02-20T10:30:00Z" },
  { id: "comp-2", username: "rival_store", display_name: "Rival Store Official", follower_count: 1_890_000, following_count: 156, video_count: 324, last_synced: "2026-02-20T09:15:00Z" },
  { id: "comp-3", username: "topshop_tt", display_name: "TopShop TikTok", follower_count: 980_000, following_count: 89, video_count: 215, last_synced: "2026-02-19T22:00:00Z" },
  { id: "comp-4", username: "beautyco_official", display_name: "BeautyCo", follower_count: 3_120_000, following_count: 201, video_count: 612, last_synced: "2026-02-20T08:45:00Z" },
  { id: "comp-5", username: "gadgets_world", display_name: "Gadgets World", follower_count: 760_000, following_count: 45, video_count: 178, last_synced: "2026-02-19T18:30:00Z" },
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
  const [search, setSearch] = useState("");

  function handleAdd() {
    if (!newUsername.trim()) return;
    toast.success(`Now tracking @${newUsername.trim()}`);
    setNewUsername("");
    setShowAdd(false);
  }

  const totalFollowers = competitors.reduce((sum, c) => sum + c.follower_count, 0);
  const totalVideos = competitors.reduce((sum, c) => sum + c.video_count, 0);

  const columns: Column<Competitor>[] = [
    {
      key: "competitor",
      header: "Competitor",
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 text-sm font-medium">
            {row.display_name[0]}
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">{row.display_name}</p>
            <p className="text-xs text-gray-500">@{row.username}</p>
          </div>
        </div>
      ),
    },
    {
      key: "followers",
      header: "Followers",
      render: (row) => (
        <div className="flex items-center gap-1.5">
          <Users className="h-3.5 w-3.5 text-gray-400" />
          <span className="text-sm text-gray-600">{formatNumber(row.follower_count)}</span>
        </div>
      ),
    },
    {
      key: "videos",
      header: "Videos",
      render: (row) => <span className="text-sm text-gray-600">{row.video_count}</span>,
    },
    {
      key: "last_synced",
      header: "Last Synced",
      render: (row) => (
        <div className="flex items-center gap-1.5">
          <Clock className="h-3.5 w-3.5 text-gray-400" />
          <span className="text-sm text-gray-500">{new Date(row.last_synced).toLocaleDateString()}</span>
        </div>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      className: "w-24",
      render: (row) => (
        <Link href={`/intelligence/competitors/${row.id}`} className="flex items-center gap-1 text-sm text-blue-600 hover:underline">
          <Eye className="h-3.5 w-3.5" />
          View
        </Link>
      ),
    },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Tracked Competitors" value={competitors.length} icon={Eye} />
          <MetricCard label="Combined Followers" value={formatNumber(totalFollowers)} icon={Users} />
          <MetricCard label="Total Videos" value={formatNumber(totalVideos)} icon={Film} />
          <MetricCard label="Last Sync" value="Today" icon={Clock} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Top competitor" description="BeautyCo leads with 3.1M followers and 612 videos. Monitor their content strategy." variant="default" />
          <InsightItem title="Gap analysis" description="Brand Alpha posts 3x more frequently than your account. Consider increasing content output." variant="warning" />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search competitors..."
        actions={
          <button
            onClick={() => setShowAdd(true)}
            className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 transition-colors"
          >
            Add Competitor
          </button>
        }
      />

      <DataTable
        columns={columns}
        data={competitors.filter((c) => !search || c.display_name.toLowerCase().includes(search.toLowerCase()) || c.username.toLowerCase().includes(search.toLowerCase()))}
        keyExtractor={(row) => row.id}
        emptyTitle="No competitors tracked"
        emptyDescription="Add a competitor to start monitoring their TikTok activity"
        emptyAction={{ label: "Add Competitor", onClick: () => setShowAdd(true) }}
      />

      <Modal open={showAdd} onClose={() => setShowAdd(false)} title="Add Competitor">
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">TikTok Username *</label>
            <input
              type="text"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAdd()}
              placeholder="@brandname"
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button onClick={() => setShowAdd(false)} className="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50">Cancel</button>
            <button onClick={handleAdd} disabled={!newUsername.trim()} className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 disabled:opacity-50">Track</button>
          </div>
        </div>
      </Modal>
    </PageShell>
  );
}
