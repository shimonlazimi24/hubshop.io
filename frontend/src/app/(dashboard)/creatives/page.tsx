"use client";

import { useState } from "react";
import { Layers, MousePointerClick, TrendingUp, AlertTriangle, Grid3X3, List, Play, Image as ImageIcon, LayoutGrid } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { CreativeCard } from "@/components/ui/creative-card";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { StatusBadge } from "@/components/ui/status-badge";

type CreativeFormat = "video" | "image" | "carousel";

interface Creative {
  id: string;
  title: string;
  format: CreativeFormat;
  ctr: number;
  views: number;
  roas: number;
  campaign: string;
  date: string;
}

const MOCK_CREATIVES: Creative[] = [
  { id: "1", title: "Summer Sale Hero Video", format: "video", ctr: 4.2, views: 125000, roas: 3.8, campaign: "Summer 2026", date: "2026-02-18" },
  { id: "2", title: "Product Showcase Carousel", format: "carousel", ctr: 3.1, views: 89000, roas: 2.9, campaign: "Spring Launch", date: "2026-02-17" },
  { id: "3", title: "Brand Story Image", format: "image", ctr: 2.8, views: 67000, roas: 2.1, campaign: "Brand Awareness", date: "2026-02-16" },
  { id: "4", title: "Unboxing Experience", format: "video", ctr: 5.1, views: 234000, roas: 4.5, campaign: "Summer 2026", date: "2026-02-15" },
  { id: "5", title: "Lifestyle Banner", format: "image", ctr: 1.9, views: 45000, roas: 1.7, campaign: "Brand Awareness", date: "2026-02-14" },
  { id: "6", title: "Feature Highlight Reel", format: "video", ctr: 3.7, views: 156000, roas: 3.2, campaign: "Product Launch", date: "2026-02-13" },
  { id: "7", title: "Comparison Carousel", format: "carousel", ctr: 2.5, views: 78000, roas: 2.4, campaign: "Retargeting Q1", date: "2026-02-12" },
  { id: "8", title: "Testimonial Clip", format: "video", ctr: 4.8, views: 198000, roas: 4.1, campaign: "Social Proof", date: "2026-02-11" },
  { id: "9", title: "Holiday Promo Banner", format: "image", ctr: 3.3, views: 92000, roas: 2.7, campaign: "Holiday 2026", date: "2026-02-10" },
  { id: "10", title: "Behind the Scenes", format: "video", ctr: 3.9, views: 143000, roas: 3.0, campaign: "Brand Awareness", date: "2026-02-09" },
  { id: "11", title: "Multi-Product Showcase", format: "carousel", ctr: 2.2, views: 54000, roas: 2.0, campaign: "Spring Launch", date: "2026-02-08" },
  { id: "12", title: "Flash Sale Announcement", format: "video", ctr: 6.1, views: 312000, roas: 5.2, campaign: "Flash Sale Feb", date: "2026-02-07" },
];

const FORMAT_OPTIONS = [
  { label: "Video", value: "video" },
  { label: "Image", value: "image" },
  { label: "Carousel", value: "carousel" },
];

const SORT_OPTIONS = [
  { label: "Best CTR", value: "ctr" },
  { label: "Most Views", value: "views" },
  { label: "Newest", value: "date" },
];

const FORMAT_ICON: Record<CreativeFormat, typeof Play> = {
  video: Play,
  image: ImageIcon,
  carousel: LayoutGrid,
};

const TABLE_COLUMNS: Column<Creative>[] = [
  {
    key: "title",
    header: "Title",
    sortable: true,
    render: (row) => (
      <div className="flex items-center gap-2">
        <div className="h-8 w-8 rounded bg-gray-100 flex items-center justify-center flex-shrink-0">
          {(() => { const Icon = FORMAT_ICON[row.format]; return <Icon className="h-4 w-4 text-gray-400" />; })()}
        </div>
        <span className="font-medium text-gray-900">{row.title}</span>
      </div>
    ),
  },
  {
    key: "format",
    header: "Format",
    render: (row) => (
      <StatusBadge
        variant={row.format === "video" ? "active" : row.format === "image" ? "syncing" : "warning"}
        label={row.format.charAt(0).toUpperCase() + row.format.slice(1)}
      />
    ),
  },
  {
    key: "ctr",
    header: "CTR",
    sortable: true,
    render: (row) => <span className="tabular-nums">{row.ctr.toFixed(1)}%</span>,
  },
  {
    key: "views",
    header: "Views",
    sortable: true,
    render: (row) => <span className="tabular-nums">{row.views.toLocaleString()}</span>,
  },
  {
    key: "roas",
    header: "ROAS",
    sortable: true,
    render: (row) => <span className="tabular-nums">{row.roas.toFixed(1)}x</span>,
  },
  {
    key: "campaign",
    header: "Campaign",
    render: (row) => <span className="text-gray-600">{row.campaign}</span>,
  },
  {
    key: "date",
    header: "Date",
    sortable: true,
    render: (row) => <span className="text-gray-500 tabular-nums">{row.date}</span>,
  },
];

export default function CreativeLibraryPage() {
  const [search, setSearch] = useState("");
  const [formatFilter, setFormatFilter] = useState("");
  const [sortBy, setSortBy] = useState("");
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");

  const filtered = MOCK_CREATIVES.filter((c) => {
    if (search && !c.title.toLowerCase().includes(search.toLowerCase())) return false;
    if (formatFilter && c.format !== formatFilter) return false;
    return true;
  }).sort((a, b) => {
    if (sortBy === "ctr") return b.ctr - a.ctr;
    if (sortBy === "views") return b.views - a.views;
    if (sortBy === "date") return b.date.localeCompare(a.date);
    return 0;
  });

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Total Creatives"
            value={12}
            icon={Layers}
            trend={{ value: 20, direction: "up", label: "vs last month" }}
            sparklineData={[6, 7, 8, 8, 9, 10, 12]}
          />
          <MetricCard
            label="Avg CTR"
            value="3.6%"
            icon={MousePointerClick}
            trend={{ value: 8.3, direction: "up", label: "vs last month" }}
            sparklineData={[2.8, 3.0, 3.1, 3.2, 3.4, 3.5, 3.6]}
          />
          <MetricCard
            label="Top ROAS"
            value="5.2x"
            icon={TrendingUp}
            trend={{ value: 15.6, direction: "up", label: "vs last month" }}
            sparklineData={[3.2, 3.5, 3.8, 4.1, 4.5, 4.8, 5.2]}
          />
          <MetricCard
            label="Fatigued"
            value={2}
            icon={AlertTriangle}
            iconColor="text-warning"
            trend={{ value: 1, direction: "up", label: "needs refresh" }}
          />
        </MetricBar>
      }
      aside={
        <InsightPanel defaultOpen>
          <InsightItem
            icon={<TrendingUp className="h-4 w-4 text-success" />}
            title="Top Performer"
            description="'Flash Sale Announcement' has 6.1% CTR and 5.2x ROAS — consider scaling this creative to more campaigns."
            variant="success"
            action={{ label: "View creative", onClick: () => {} }}
          />
          <InsightItem
            icon={<AlertTriangle className="h-4 w-4 text-warning" />}
            title="Fatigue Alert"
            description="'Lifestyle Banner' and 'Multi-Product Showcase' show declining engagement. Consider refreshing or replacing."
            variant="warning"
            action={{ label: "View fatigued", onClick: () => {} }}
          />
          <InsightItem
            icon={<Play className="h-4 w-4 text-info" />}
            title="Best Format"
            description="Video creatives average 4.3% CTR vs 2.7% for images. Focus on video-first creative strategy."
            variant="default"
          />
        </InsightPanel>
      }
    >
      <FilterBar
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search creatives..."
        actions={
          <div className="flex items-center gap-1 rounded-lg border border-gray-200 p-0.5">
            <button
              onClick={() => setViewMode("grid")}
              className={`flex h-7 w-7 items-center justify-center rounded-md transition-colors ${
                viewMode === "grid" ? "bg-gray-100 text-gray-900" : "text-gray-400 hover:text-gray-600"
              }`}
            >
              <Grid3X3 className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setViewMode("table")}
              className={`flex h-7 w-7 items-center justify-center rounded-md transition-colors ${
                viewMode === "table" ? "bg-gray-100 text-gray-900" : "text-gray-400 hover:text-gray-600"
              }`}
            >
              <List className="h-3.5 w-3.5" />
            </button>
          </div>
        }
      >
        <FilterDropdown
          label="All Formats"
          value={formatFilter}
          options={FORMAT_OPTIONS}
          onChange={setFormatFilter}
        />
        <FilterDropdown
          label="Sort by"
          value={sortBy}
          options={SORT_OPTIONS}
          onChange={setSortBy}
        />
      </FilterBar>

      {viewMode === "grid" ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {filtered.map((creative) => (
            <CreativeCard
              key={creative.id}
              title={creative.title}
              format={creative.format}
              metrics={[
                { label: "CTR", value: `${creative.ctr.toFixed(1)}%` },
                { label: "Views", value: creative.views >= 1000 ? `${(creative.views / 1000).toFixed(0)}K` : String(creative.views) },
                { label: "ROAS", value: `${creative.roas.toFixed(1)}x` },
              ]}
              onClick={() => {}}
            />
          ))}
        </div>
      ) : (
        <DataTable
          columns={TABLE_COLUMNS}
          data={filtered}
          keyExtractor={(row) => row.id}
          onRowClick={() => {}}
          emptyTitle="No creatives found"
          emptyDescription="Try adjusting your filters or search term."
        />
      )}
    </PageShell>
  );
}
