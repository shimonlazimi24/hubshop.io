"use client";

import { MousePointerClick, TrendingUp, Activity, AlertTriangle } from "lucide-react";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { ChartCard } from "@/components/ui/chart-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { StatusBadge } from "@/components/ui/status-badge";

interface PerformanceRow {
  id: string;
  rank: number;
  title: string;
  format: "video" | "image" | "carousel";
  ctr: number;
  roas: number;
  spend: number;
  views: number;
  fatigueScore: number;
}

const FORMAT_BAR_DATA = [
  { format: "Video", ctr: 4.3, roas: 3.7, engagement: 8.2 },
  { format: "Image", ctr: 2.7, roas: 2.2, engagement: 4.5 },
  { format: "Carousel", ctr: 2.6, roas: 2.4, engagement: 5.1 },
];

const FATIGUE_TIMELINE = [
  { date: "Jan 1", score: 12 },
  { date: "Jan 8", score: 15 },
  { date: "Jan 15", score: 18 },
  { date: "Jan 22", score: 22 },
  { date: "Jan 29", score: 25 },
  { date: "Feb 5", score: 28 },
  { date: "Feb 12", score: 32 },
  { date: "Feb 19", score: 35 },
];

const RANKING_DATA: PerformanceRow[] = [
  { id: "1", rank: 1, title: "Flash Sale Announcement", format: "video", ctr: 6.1, roas: 5.2, spend: 2400, views: 312000, fatigueScore: 8 },
  { id: "2", rank: 2, title: "Unboxing Experience", format: "video", ctr: 5.1, roas: 4.5, spend: 1800, views: 234000, fatigueScore: 15 },
  { id: "3", rank: 3, title: "Testimonial Clip", format: "video", ctr: 4.8, roas: 4.1, spend: 1500, views: 198000, fatigueScore: 22 },
  { id: "4", rank: 4, title: "Summer Sale Hero Video", format: "video", ctr: 4.2, roas: 3.8, spend: 1200, views: 125000, fatigueScore: 30 },
  { id: "5", rank: 5, title: "Behind the Scenes", format: "video", ctr: 3.9, roas: 3.0, spend: 900, views: 143000, fatigueScore: 18 },
  { id: "6", rank: 6, title: "Feature Highlight Reel", format: "video", ctr: 3.7, roas: 3.2, spend: 1100, views: 156000, fatigueScore: 45 },
  { id: "7", rank: 7, title: "Holiday Promo Banner", format: "image", ctr: 3.3, roas: 2.7, spend: 700, views: 92000, fatigueScore: 52 },
  { id: "8", rank: 8, title: "Product Showcase Carousel", format: "carousel", ctr: 3.1, roas: 2.9, spend: 650, views: 89000, fatigueScore: 28 },
  { id: "9", rank: 9, title: "Brand Story Image", format: "image", ctr: 2.8, roas: 2.1, spend: 500, views: 67000, fatigueScore: 60 },
  { id: "10", rank: 10, title: "Comparison Carousel", format: "carousel", ctr: 2.5, roas: 2.4, spend: 450, views: 78000, fatigueScore: 35 },
];

const RANKING_COLUMNS: Column<PerformanceRow>[] = [
  {
    key: "rank",
    header: "Rank",
    className: "w-16",
    render: (row) => (
      <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-gray-100 text-xs font-bold text-gray-700">
        {row.rank}
      </span>
    ),
  },
  {
    key: "title",
    header: "Title",
    sortable: true,
    render: (row) => <span className="font-medium text-gray-900">{row.title}</span>,
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
    key: "roas",
    header: "ROAS",
    sortable: true,
    render: (row) => <span className="tabular-nums">{row.roas.toFixed(1)}x</span>,
  },
  {
    key: "spend",
    header: "Spend",
    sortable: true,
    render: (row) => <span className="tabular-nums">${row.spend.toLocaleString()}</span>,
  },
  {
    key: "views",
    header: "Views",
    sortable: true,
    render: (row) => <span className="tabular-nums">{row.views.toLocaleString()}</span>,
  },
  {
    key: "fatigueScore",
    header: "Fatigue",
    sortable: true,
    render: (row) => {
      const variant = row.fatigueScore < 25 ? "active" : row.fatigueScore < 50 ? "warning" : "error";
      return <StatusBadge variant={variant} label={`${row.fatigueScore}%`} />;
    },
  },
];

export default function CreativePerformancePage() {
  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Avg CTR"
            value="3.6%"
            icon={MousePointerClick}
            trend={{ value: 8.3, direction: "up", label: "vs last month" }}
            sparklineData={[2.8, 3.0, 3.1, 3.2, 3.4, 3.5, 3.6]}
          />
          <MetricCard
            label="Avg ROAS"
            value="3.2x"
            icon={TrendingUp}
            trend={{ value: 5.1, direction: "up", label: "vs last month" }}
            sparklineData={[2.5, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2]}
          />
          <MetricCard
            label="Avg Engagement"
            value="6.4%"
            icon={Activity}
            trend={{ value: 3.2, direction: "up", label: "vs last month" }}
            sparklineData={[5.2, 5.5, 5.7, 5.9, 6.1, 6.2, 6.4]}
          />
          <MetricCard
            label="Fatigue Rate"
            value="35%"
            icon={AlertTriangle}
            iconColor="text-warning"
            trend={{ value: 12, direction: "up", label: "increasing" }}
            sparklineData={[18, 20, 22, 25, 28, 32, 35]}
          />
        </MetricBar>
      }
      aside={
        <InsightPanel defaultOpen>
          <InsightItem
            icon={<TrendingUp className="h-4 w-4 text-success" />}
            title="Best Performing Format"
            description="Video creatives outperform other formats with 4.3% avg CTR and 3.7x ROAS. Allocate more budget to video."
            variant="success"
            action={{ label: "View videos", onClick: () => {} }}
          />
          <InsightItem
            icon={<AlertTriangle className="h-4 w-4 text-warning" />}
            title="Creatives Needing Refresh"
            description="3 creatives have fatigue scores above 50%. Replace or refresh 'Brand Story Image', 'Holiday Promo Banner', and 'Feature Highlight Reel'."
            variant="warning"
            action={{ label: "View fatigued", onClick: () => {} }}
          />
          <InsightItem
            icon={<Activity className="h-4 w-4 text-info" />}
            title="A/B Test Opportunities"
            description="'Summer Sale Hero Video' and 'Behind the Scenes' target similar audiences. Run an A/B test to find the winner."
            variant="default"
            action={{ label: "Create test", onClick: () => {} }}
          />
        </InsightPanel>
      }
    >
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <ChartCard title="Performance by Format">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={FORMAT_BAR_DATA} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="format" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ borderRadius: 8, border: "1px solid #e5e7eb", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="ctr" name="CTR %" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="roas" name="ROAS x" fill="var(--chart-2)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="engagement" name="Engagement %" fill="var(--chart-3)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Creative Fatigue Timeline">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={FATIGUE_TIMELINE} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ borderRadius: 8, border: "1px solid #e5e7eb", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }}
              />
              <Line
                type="monotone"
                dataKey="score"
                name="Fatigue Score %"
                stroke="var(--chart-5)"
                strokeWidth={2}
                dot={{ fill: "var(--chart-5)", r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <h3 className="text-sm font-semibold text-gray-900 mb-3">Creative Performance Ranking</h3>
      <DataTable
        columns={RANKING_COLUMNS}
        data={RANKING_DATA}
        keyExtractor={(row) => row.id}
        onRowClick={() => {}}
        emptyTitle="No performance data"
        emptyDescription="Performance data will appear once creatives have been running."
      />
    </PageShell>
  );
}
