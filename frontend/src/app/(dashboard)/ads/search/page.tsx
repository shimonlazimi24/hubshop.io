"use client";

import { useState } from "react";
import {
  Search,
  Ban,
  Star,
  HeartPulse,
  Plus,
  X,
  TrendingUp,
  TrendingDown,
  Trophy,
  AlertTriangle,
  Target,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";

interface KeywordResult {
  keyword: string;
  volume: number;
  competition: "Low" | "Medium" | "High";
  cpc: number;
  trend: number;
}

const MOCK_KEYWORD_RESULTS: KeywordResult[] = [
  { keyword: "skincare routine", volume: 1_240_000, competition: "High", cpc: 2.45, trend: 12.3 },
  { keyword: "best moisturizer", volume: 890_000, competition: "High", cpc: 3.12, trend: 8.7 },
  { keyword: "vitamin c serum", volume: 720_000, competition: "Medium", cpc: 1.98, trend: 15.1 },
  { keyword: "sunscreen spf 50", volume: 540_000, competition: "Medium", cpc: 1.65, trend: 22.4 },
  { keyword: "acne treatment", volume: 430_000, competition: "Low", cpc: 0.89, trend: -3.2 },
  { keyword: "korean skincare", volume: 380_000, competition: "Low", cpc: 1.12, trend: 18.9 },
];

const MOCK_NEGATIVE_KEYWORDS = [
  { id: "nk-1", keyword: "free", added: "2026-02-10" },
  { id: "nk-2", keyword: "cheap", added: "2026-02-10" },
  { id: "nk-3", keyword: "diy", added: "2026-02-12" },
  { id: "nk-4", keyword: "homemade", added: "2026-02-14" },
  { id: "nk-5", keyword: "coupon", added: "2026-02-18" },
];

interface CampaignHealth {
  id: string;
  name: string;
  score: number;
  issues: string[];
  status: "healthy" | "warning" | "critical";
}

const MOCK_CAMPAIGN_HEALTH: CampaignHealth[] = [
  { id: "ch-1", name: "Brand Awareness Q1", score: 95, issues: [], status: "healthy" },
  { id: "ch-2", name: "Product Launch Feb", score: 78, issues: ["Low quality score on 3 keywords"], status: "warning" },
  { id: "ch-3", name: "Retargeting - Cart", score: 92, issues: [], status: "healthy" },
  { id: "ch-4", name: "Competitor Conquest", score: 54, issues: ["High CPC", "Low CTR", "Budget overspend"], status: "critical" },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return String(n);
}

export default function SearchAdsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [showResults, setShowResults] = useState(false);
  const [newNegative, setNewNegative] = useState("");

  function handleSearch() {
    if (!searchQuery.trim()) return;
    setShowResults(true);
  }

  const keywordColumns: Column<KeywordResult>[] = [
    {
      key: "keyword",
      header: "Keyword",
      sortable: true,
      render: (row) => <span className="text-sm font-medium text-gray-900">{row.keyword}</span>,
    },
    {
      key: "volume",
      header: "Volume",
      sortable: true,
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{formatNumber(row.volume)}</span>,
    },
    {
      key: "competition",
      header: "Competition",
      render: (row) => (
        <StatusBadge
          variant={row.competition === "High" ? "error" : row.competition === "Medium" ? "warning" : "active"}
          label={row.competition}
        />
      ),
    },
    {
      key: "cpc",
      header: "CPC",
      sortable: true,
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">${row.cpc.toFixed(2)}</span>,
    },
    {
      key: "trend",
      header: "Trend",
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-1">
          {row.trend >= 0 ? (
            <TrendingUp className="h-3.5 w-3.5 text-success" />
          ) : (
            <TrendingDown className="h-3.5 w-3.5 text-danger" />
          )}
          <span className={cn("text-sm font-medium tabular-nums", row.trend >= 0 ? "text-success" : "text-danger")}>
            {row.trend >= 0 ? "+" : ""}{row.trend}%
          </span>
        </div>
      ),
    },
  ];

  return (
    <>
      <PageHeader title="Search Ads" description="Keyword research, negative keywords, and campaign health" />
      <PageShell
        header={
          <MetricBar>
            <MetricCard label="Keywords Tracked" value={128} icon={Search} iconColor="text-purple" trend={{ value: 12, direction: "up", label: "this month" }} />
            <MetricCard label="Negative Keywords" value={34} icon={Ban} iconColor="text-coral" />
            <MetricCard label="Avg Quality Score" value="7.4" icon={Star} iconColor="text-success" trend={{ value: 0.3, direction: "up", label: "vs last week" }} />
            <MetricCard label="Campaign Health" value="92%" icon={HeartPulse} iconColor="text-info" />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<Trophy className="h-4 w-4 text-success" />}
              title="Top Keyword"
              description="'skincare routine' has the highest volume with strong upward trend (+12.3%)."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-danger" />}
              title="Campaign Alert"
              description="'Competitor Conquest' has a critical health score of 54. Review immediately."
              variant="danger"
              action={{ label: "Review campaign", onClick: () => {} }}
            />
            <InsightItem
              icon={<Target className="h-4 w-4 text-info" />}
              title="Negative Keywords"
              description="Adding 'discount' and 'sample' as negative keywords could save ~$200/week."
              variant="default"
            />
          </InsightPanel>
        }
      >
        {/* Keyword Research Tool */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">Keyword Research Tool</h2>
          <div className="rounded-xl border border-gray-100 bg-white p-5">
            <div className="flex gap-3 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  placeholder="Search keywords (e.g., skincare, fitness, cooking)"
                  className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
                />
              </div>
              <button
                onClick={handleSearch}
                className="flex items-center gap-1.5 rounded-lg bg-coral px-4 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
              >
                <Search className="h-4 w-4" />
                Research
              </button>
            </div>

            {showResults && (
              <DataTable
                columns={keywordColumns}
                data={MOCK_KEYWORD_RESULTS}
                keyExtractor={(row) => row.keyword}
                emptyTitle="No keywords found"
              />
            )}
          </div>
        </div>

        {/* Negative Keywords Management */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">Negative Keywords</h2>
          <div className="rounded-xl border border-gray-100 bg-white p-5">
            <div className="flex gap-3 mb-4">
              <input
                type="text"
                value={newNegative}
                onChange={(e) => setNewNegative(e.target.value)}
                placeholder="Add a negative keyword"
                className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
              />
              <button
                onClick={() => setNewNegative("")}
                disabled={!newNegative.trim()}
                className="flex items-center gap-1.5 rounded-lg bg-gray-900 px-3 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 transition-colors"
              >
                <Plus className="h-4 w-4" />
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {MOCK_NEGATIVE_KEYWORDS.map((nk) => (
                <span
                  key={nk.id}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-danger/5 text-danger rounded-full text-sm border border-danger/10"
                >
                  <Ban className="h-3 w-3" />
                  {nk.keyword}
                  <button className="ml-0.5 hover:text-danger/80">
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Campaign Health Cards */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">Campaign Health</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {MOCK_CAMPAIGN_HEALTH.map((campaign) => (
              <div
                key={campaign.id}
                className="rounded-xl border border-gray-100 bg-white p-5 shadow-[var(--shadow-card)]"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-gray-900">{campaign.name}</h3>
                  <StatusBadge
                    variant={campaign.status === "healthy" ? "active" : campaign.status === "warning" ? "warning" : "error"}
                    label={campaign.status === "healthy" ? "Healthy" : campaign.status === "warning" ? "Warning" : "Critical"}
                  />
                </div>
                <div className="flex items-center gap-3 mb-2">
                  <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={cn(
                        "h-full rounded-full transition-all",
                        campaign.score >= 80 ? "bg-success" : campaign.score >= 60 ? "bg-warning" : "bg-danger"
                      )}
                      style={{ width: `${campaign.score}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-gray-900 tabular-nums">{campaign.score}</span>
                </div>
                {campaign.issues.length > 0 && (
                  <ul className="mt-2 space-y-1">
                    {campaign.issues.map((issue, i) => (
                      <li key={i} className="text-xs text-gray-500 flex items-center gap-1.5">
                        <span className="h-1 w-1 rounded-full bg-gray-400" />
                        {issue}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      </PageShell>
    </>
  );
}
