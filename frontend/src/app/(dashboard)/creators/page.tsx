"use client";

import { useEffect, useState } from "react";
import { Users, TrendingUp, Heart, Search as SearchIcon, Star } from "lucide-react";
import { discoverCreators, listCreatorProfiles, saveCreator, type CreatorSummary, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { EmptyState } from "@/components/ui/empty-state";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const TIER_VARIANT: Record<string, StatusVariant> = {
  NANO: "draft",
  MICRO: "syncing",
  MID: "warning",
  MACRO: "active",
  MEGA: "error",
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
      .catch(() => toast.error("Failed to load creator profiles"))
      .finally(() => setLoading(false));
  }

  async function handleSearch() {
    if (!token || !query.trim()) return;
    setSearching(true);
    try {
      const result = await discoverCreators(WORKSPACE_ID, { query: query.trim() }, token);
      setDiscoveryResults(result.creators);
      toast.success(`Found ${result.creators.length} creators`);
    } catch {
      toast.error("Search failed. Please try again.");
    } finally {
      setSearching(false);
    }
  }

  async function handleSave(creatorId: string, isSaved: boolean) {
    if (!token) return;
    try {
      await saveCreator(creatorId, !isSaved, token);
      toast.success(isSaved ? "Creator removed from saved" : "Creator saved");
      if (tab === "saved") loadProfiles();
    } catch {
      toast.error("Failed to update saved status");
    }
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: "discover", label: "Search TTCM" },
    { key: "saved", label: "Saved Creators" },
  ];

  const savedColumns: Column<CreatorSummary>[] = [
    {
      key: "creator",
      header: "Creator",
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-xs font-medium">
            {(row.display_name || row.username || "?")[0]}
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">{row.display_name || "Unknown"}</p>
            <p className="text-xs text-gray-500">@{row.username || "-"}</p>
          </div>
        </div>
      ),
    },
    {
      key: "tier",
      header: "Tier",
      render: (row) =>
        row.tier ? (
          <StatusBadge variant={TIER_VARIANT[row.tier] || "draft"} label={row.tier} />
        ) : (
          <span className="text-gray-400">-</span>
        ),
    },
    {
      key: "followers",
      header: "Followers",
      sortable: true,
      render: (row) => <span className="text-sm tabular-nums">{row.follower_count.toLocaleString()}</span>,
    },
    {
      key: "engagement",
      header: "Engagement",
      sortable: true,
      render: (row) => (
        <span className="text-sm tabular-nums">
          {row.engagement_rate ? `${row.engagement_rate}%` : "-"}
        </span>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (row) => (
        <button
          onClick={(e) => { e.stopPropagation(); handleSave(row.id, row.is_saved); }}
          className="text-sm text-danger hover:underline"
        >
          Unsave
        </button>
      ),
    },
  ];

  const discoverColumns: Column<Record<string, unknown>>[] = [
    {
      key: "creator",
      header: "Creator",
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-xs font-medium">
            {((row.display_name as string) || "?")[0]}
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">{(row.display_name as string) || "Unknown"}</p>
            <p className="text-xs text-gray-500">@{(row.username as string) || "-"}</p>
          </div>
        </div>
      ),
    },
    {
      key: "followers",
      header: "Followers",
      sortable: true,
      render: (row) => (
        <span className="text-sm tabular-nums">
          {((row.follower_count as number) || 0).toLocaleString()}
        </span>
      ),
    },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Total Saved" value={profiles?.total ?? 0} icon={Users} trend={{ value: 12, direction: "up", label: "vs last month" }} />
          <MetricCard label="Avg Engagement" value="4.8%" icon={TrendingUp} trend={{ value: 0.3, direction: "up" }} />
          <MetricCard label="Top Tier" value="Macro" icon={Star} />
          <MetricCard label="Campaigns Active" value={3} icon={Heart} trend={{ value: 1, direction: "up" }} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem
            title="High engagement creator"
            description="@cook_with_emma has 7.1% engagement rate — ideal for product features."
            variant="success"
            action={{ label: "View profile", onClick: () => {} }}
          />
          <InsightItem
            title="Trending niche"
            description="Beauty creators showing +24% engagement growth this month."
            variant="warning"
          />
          <InsightItem
            title="New opportunity"
            description="3 nano creators in your niche gained 10K+ followers this week."
            action={{ label: "Discover", onClick: () => setTab("discover") }}
          />
        </InsightPanel>
      }
    >
      <div className="flex gap-2 mb-4">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => { setTab(t.key); setPage(1); }}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${tab === t.key ? "bg-gray-900 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "discover" && (
        <div>
          <FilterBar
            searchValue={query}
            onSearchChange={setQuery}
            searchPlaceholder="Search creators by keyword..."
            actions={
              <button
                onClick={handleSearch}
                disabled={searching}
                className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 disabled:opacity-50 transition-colors"
              >
                {searching ? "Searching..." : "Search TTCM"}
              </button>
            }
          />

          {discoveryResults.length > 0 ? (
            <DataTable
              columns={discoverColumns}
              data={discoveryResults}
              keyExtractor={(row) => JSON.stringify(row)}
              emptyTitle="No creators found"
              emptyDescription="Try a different search keyword"
            />
          ) : (
            <EmptyState
              icon={SearchIcon}
              title="Search the TikTok Creator Marketplace"
              description="Enter a keyword to discover creators matching your brand"
            />
          )}
          {searching && <div className="text-center py-8 text-gray-500">Searching creators...</div>}
        </div>
      )}

      {tab === "saved" && (
        <DataTable
          columns={savedColumns}
          data={profiles?.items ?? []}
          keyExtractor={(row) => row.id}
          loading={loading}
          page={page}
          totalPages={profiles?.total_pages ?? 1}
          onPageChange={setPage}
          emptyTitle="No saved creators"
          emptyDescription="Save creators from the discovery tab to see them here"
          emptyAction={{ label: "Discover Creators", onClick: () => setTab("discover") }}
        />
      )}
    </PageShell>
  );
}
