"use client";

import { useState } from "react";
import { Hash, Music, ShoppingBag, TrendingUp } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { cn } from "@/lib/utils";

type TrendTab = "hashtags" | "sounds" | "products";

interface TrendItem {
  rank: number;
  name: string;
  metric: number;
  growth: number;
}

const MOCK_HASHTAGS: TrendItem[] = [
  { rank: 1, name: "#TikTokMadeMeBuyIt", metric: 52_400_000_000, growth: 12.4 },
  { rank: 2, name: "#GRWM", metric: 41_200_000_000, growth: 8.7 },
  { rank: 3, name: "#SmallBusiness", metric: 38_900_000_000, growth: 15.2 },
  { rank: 4, name: "#BookTok", metric: 34_100_000_000, growth: 6.1 },
  { rank: 5, name: "#FYP", metric: 29_800_000_000, growth: -2.3 },
  { rank: 6, name: "#LifeHack", metric: 27_500_000_000, growth: 9.8 },
  { rank: 7, name: "#OOTD", metric: 24_300_000_000, growth: 4.5 },
  { rank: 8, name: "#Recipe", metric: 21_700_000_000, growth: 11.3 },
];

const MOCK_SOUNDS: TrendItem[] = [
  { rank: 1, name: "Original Sound - @creator1", metric: 2_340_000, growth: 45.2 },
  { rank: 2, name: "Trending Beat #42", metric: 1_890_000, growth: 32.1 },
  { rank: 3, name: "Viral Audio Clip", metric: 1_560_000, growth: 28.7 },
  { rank: 4, name: "Popular Song Remix", metric: 1_230_000, growth: 15.4 },
  { rank: 5, name: "Comedy Skit Sound", metric: 980_000, growth: 22.3 },
  { rank: 6, name: "Dance Challenge Beat", metric: 870_000, growth: 19.8 },
];

const MOCK_PRODUCTS: TrendItem[] = [
  { rank: 1, name: "LED Strip Lights", metric: 145_000, growth: 34.5 },
  { rank: 2, name: "Portable Blender", metric: 128_000, growth: 28.9 },
  { rank: 3, name: "Phone Ring Light", metric: 112_000, growth: 21.3 },
  { rank: 4, name: "Skincare Serum Set", metric: 98_000, growth: 18.7 },
  { rank: 5, name: "Wireless Earbuds", metric: 87_000, growth: 12.4 },
  { rank: 6, name: "Mini Projector", metric: 76_000, growth: 25.6 },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)}B`;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

const TAB_ICONS: Record<TrendTab, typeof Hash> = {
  hashtags: Hash,
  sounds: Music,
  products: ShoppingBag,
};

const METRIC_LABELS: Record<TrendTab, string> = {
  hashtags: "Views",
  sounds: "Uses",
  products: "Orders",
};

export default function TrendsPage() {
  const [tab, setTab] = useState<TrendTab>("hashtags");
  const [region, setRegion] = useState("");
  const [search, setSearch] = useState("");

  const data = tab === "hashtags" ? MOCK_HASHTAGS : tab === "sounds" ? MOCK_SOUNDS : MOCK_PRODUCTS;
  const Icon = TAB_ICONS[tab];

  const columns: Column<TrendItem>[] = [
    {
      key: "rank",
      header: "Rank",
      className: "w-16",
      render: (row) => (
        <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-gray-100 text-xs font-semibold text-gray-700">
          {row.rank}
        </span>
      ),
    },
    {
      key: "name",
      header: tab === "hashtags" ? "Hashtag" : tab === "sounds" ? "Sound" : "Product",
      render: (row) => (
        <div className="flex items-center gap-2">
          <Icon className={cn("h-4 w-4", tab === "hashtags" ? "text-purple" : tab === "sounds" ? "text-cyan" : "text-emerald-500")} />
          <span className="text-sm font-medium text-gray-900">{row.name}</span>
        </div>
      ),
    },
    {
      key: "metric",
      header: METRIC_LABELS[tab],
      render: (row) => <span className="text-sm text-gray-600">{formatNumber(row.metric)}</span>,
    },
    {
      key: "growth",
      header: "Growth",
      render: (row) => (
        <div className="flex items-center gap-1">
          <TrendingUp className={cn("h-3.5 w-3.5", row.growth >= 0 ? "text-green-500" : "text-red-500")} />
          <span className={cn("text-sm font-medium", row.growth >= 0 ? "text-green-600" : "text-red-600")}>
            {row.growth >= 0 ? "+" : ""}{row.growth}%
          </span>
        </div>
      ),
    },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Total Hashtags" value={142} icon={Hash} trend={{ value: 8, direction: "up" }} />
          <MetricCard label="Trending Sounds" value={38} icon={Music} />
          <MetricCard label="Hot Products" value={24} icon={ShoppingBag} trend={{ value: 15, direction: "up" }} />
          <MetricCard label="Avg. Growth" value="18.2%" icon={TrendingUp} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Rising trend" description="#SmallBusiness is growing 15.2% week-over-week. Great opportunity for brand content." variant="success" />
          <InsightItem title="Declining hashtag" description="#FYP is down 2.3%. Consider diversifying your hashtag strategy." variant="warning" />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder={`Search ${tab}...`}
        actions={
          <div className="flex gap-2">
            {(["hashtags", "sounds", "products"] as TrendTab[]).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors",
                  tab === t
                    ? "bg-gray-900 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                )}
              >
                {TAB_ICONS[t] && (() => { const TabIcon = TAB_ICONS[t]; return <TabIcon className="h-3.5 w-3.5" />; })()}
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>
        }
      >
        <FilterDropdown
          label="Region"
          value={region}
          onChange={setRegion}
          options={[
            { label: "United States", value: "US" },
            { label: "United Kingdom", value: "GB" },
            { label: "Indonesia", value: "ID" },
            { label: "Thailand", value: "TH" },
            { label: "Vietnam", value: "VN" },
            { label: "Malaysia", value: "MY" },
            { label: "Philippines", value: "PH" },
            { label: "Singapore", value: "SG" },
          ]}
        />
      </FilterBar>

      <DataTable
        columns={columns}
        data={data.filter((item) => !search || item.name.toLowerCase().includes(search.toLowerCase()))}
        keyExtractor={(row) => String(row.rank)}
        emptyTitle="No trends found"
        emptyDescription="Try adjusting your filters"
      />
    </PageShell>
  );
}
