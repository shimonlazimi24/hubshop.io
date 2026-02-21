"use client";

import { useState } from "react";
import { Users, TrendingUp, Eye } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";

interface ScoutedCreator {
  id: string;
  username: string;
  display_name: string;
  niche: string;
  follower_count: number;
  engagement_rate: number;
  avg_views: number;
}

const MOCK_CREATORS: ScoutedCreator[] = [
  { id: "sc-1", username: "beauty_guru_tt", display_name: "Sarah Beauty", niche: "Beauty", follower_count: 245_000, engagement_rate: 6.8, avg_views: 42_000 },
  { id: "sc-2", username: "fit_lifestyle", display_name: "Mike Fitness", niche: "Fitness", follower_count: 890_000, engagement_rate: 4.2, avg_views: 120_000 },
  { id: "sc-3", username: "cook_with_emma", display_name: "Emma Cooks", niche: "Food & Cooking", follower_count: 1_200_000, engagement_rate: 7.1, avg_views: 280_000 },
  { id: "sc-4", username: "tech_reviews_daily", display_name: "TechDaily", niche: "Tech", follower_count: 560_000, engagement_rate: 3.9, avg_views: 95_000 },
  { id: "sc-5", username: "fashion_finds", display_name: "Fashion Finds", niche: "Fashion", follower_count: 178_000, engagement_rate: 8.3, avg_views: 38_000 },
  { id: "sc-6", username: "laughs_daily", display_name: "Daily Laughs", niche: "Comedy", follower_count: 2_100_000, engagement_rate: 5.6, avg_views: 450_000 },
  { id: "sc-7", username: "study_with_me", display_name: "StudyPal", niche: "Education", follower_count: 89_000, engagement_rate: 12.4, avg_views: 25_000 },
  { id: "sc-8", username: "glow_skincare", display_name: "Glow Skin", niche: "Beauty", follower_count: 340_000, engagement_rate: 5.9, avg_views: 67_000 },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export default function CreatorScoutPage() {
  const [search, setSearch] = useState("");
  const [niche, setNiche] = useState("");
  const [engagement, setEngagement] = useState("");

  const filteredCreators = MOCK_CREATORS.filter((c) => {
    if (search && !c.display_name.toLowerCase().includes(search.toLowerCase()) && !c.username.toLowerCase().includes(search.toLowerCase())) return false;
    if (niche && c.niche.toLowerCase() !== niche) return false;
    if (engagement && c.engagement_rate < Number(engagement)) return false;
    return true;
  });

  const avgEngagement = MOCK_CREATORS.reduce((sum, c) => sum + c.engagement_rate, 0) / MOCK_CREATORS.length;

  const columns: Column<ScoutedCreator>[] = [
    {
      key: "creator",
      header: "Creator",
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
      key: "niche",
      header: "Niche",
      render: (row) => <StatusBadge variant="syncing" label={row.niche} />,
    },
    {
      key: "followers",
      header: "Followers",
      render: (row) => <span className="text-sm tabular-nums">{formatNumber(row.follower_count)}</span>,
    },
    {
      key: "engagement",
      header: "Engagement",
      render: (row) => (
        <span className={`text-sm font-medium ${row.engagement_rate > 5 ? "text-green-600" : "text-gray-600"}`}>
          {row.engagement_rate}%
        </span>
      ),
    },
    {
      key: "avg_views",
      header: "Avg Views",
      render: (row) => <span className="text-sm text-gray-600">{formatNumber(row.avg_views)}</span>,
    },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Scouted Creators" value={MOCK_CREATORS.length} icon={Users} />
          <MetricCard label="Avg Engagement" value={`${avgEngagement.toFixed(1)}%`} icon={TrendingUp} trend={{ value: avgEngagement, direction: avgEngagement > 5 ? "up" : "flat" }} />
          <MetricCard label="Top Niche" value="Beauty" icon={Eye} />
          <MetricCard label="High Engagement" value={MOCK_CREATORS.filter((c) => c.engagement_rate > 5).length} icon={TrendingUp} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="High engagement alert" description="StudyPal has 12.4% engagement rate - nano-influencer with outsized impact." variant="success" />
          <InsightItem title="Niche gap" description="No lifestyle or travel creators scouted. Expand your search to diversify." variant="warning" />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search creators by name or username..."
      >
        <FilterDropdown
          label="Niche"
          value={niche}
          onChange={setNiche}
          options={[
            { label: "Beauty", value: "beauty" },
            { label: "Fashion", value: "fashion" },
            { label: "Food & Cooking", value: "food & cooking" },
            { label: "Fitness", value: "fitness" },
            { label: "Tech", value: "tech" },
            { label: "Comedy", value: "comedy" },
            { label: "Education", value: "education" },
          ]}
        />
        <FilterDropdown
          label="Min Engagement"
          value={engagement}
          onChange={setEngagement}
          options={[
            { label: "1%+", value: "1" },
            { label: "3%+", value: "3" },
            { label: "5%+", value: "5" },
            { label: "10%+", value: "10" },
          ]}
        />
      </FilterBar>

      <DataTable
        columns={columns}
        data={filteredCreators}
        keyExtractor={(row) => row.id}
        emptyTitle="No creators match"
        emptyDescription="Try adjusting your search criteria or filters"
      />
    </PageShell>
  );
}
