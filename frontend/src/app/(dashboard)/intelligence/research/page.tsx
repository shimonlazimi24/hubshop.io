"use client";

import { useState } from "react";
import { Search, Hash, User, Globe, Calendar } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";

interface ResearchResult {
  id: string;
  type: "video" | "user" | "hashtag";
  title: string;
  description: string;
  metrics: Record<string, number>;
  created_at: string;
}

const REGIONS = [
  { value: "", label: "All Regions" },
  { value: "US", label: "United States" },
  { value: "GB", label: "United Kingdom" },
  { value: "ID", label: "Indonesia" },
  { value: "TH", label: "Thailand" },
  { value: "VN", label: "Vietnam" },
  { value: "MY", label: "Malaysia" },
  { value: "PH", label: "Philippines" },
  { value: "SG", label: "Singapore" },
];

const MOCK_RESULTS: ResearchResult[] = [
  { id: "r1", type: "video", title: "Product Review: New Gadget 2026", description: "Unboxing and first impressions of the latest tech gadget trending on TikTok.", metrics: { views: 1_240_000, likes: 89_000, comments: 3_200, shares: 12_400 }, created_at: "2026-02-18T14:00:00Z" },
  { id: "r2", type: "hashtag", title: "#SpringFashion2026", description: "Trending fashion hashtag with 52M+ views in the last 7 days.", metrics: { views: 52_000_000, videos: 34_000 }, created_at: "2026-02-15T00:00:00Z" },
  { id: "r3", type: "user", title: "@trendsetter_official", description: "Fashion influencer with 1.2M followers, high engagement in beauty niche.", metrics: { followers: 1_200_000, videos: 342, avg_views: 280_000 }, created_at: "2026-02-10T00:00:00Z" },
  { id: "r4", type: "video", title: "Easy Recipe: 5-Minute Pasta", description: "Quick cooking tutorial that went viral with 3M views in 24 hours.", metrics: { views: 3_400_000, likes: 234_000, comments: 8_900, shares: 45_000 }, created_at: "2026-02-17T09:00:00Z" },
  { id: "r5", type: "hashtag", title: "#TikTokShopFinds", description: "Commerce-focused hashtag showing strong growth in SEA markets.", metrics: { views: 128_000_000, videos: 87_000 }, created_at: "2026-02-12T00:00:00Z" },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

const TYPE_MAP: Record<string, StatusVariant> = {
  video: "active",
  user: "completed",
  hashtag: "syncing",
};

export default function ResearchPage() {
  const [keyword, setKeyword] = useState("");
  const [hashtag, setHashtag] = useState("");
  const [username, setUsername] = useState("");
  const [region, setRegion] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [results, setResults] = useState<ResearchResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [searching, setSearching] = useState(false);

  function handleSearch() {
    if (!keyword.trim() && !hashtag.trim() && !username.trim()) return;
    setSearching(true);
    setTimeout(() => {
      setResults(MOCK_RESULTS);
      setHasSearched(true);
      setSearching(false);
    }, 500);
  }

  function handleClear() {
    setKeyword("");
    setHashtag("");
    setUsername("");
    setRegion("");
    setDateFrom("");
    setDateTo("");
    setResults([]);
    setHasSearched(false);
  }

  const columns: Column<ResearchResult>[] = [
    {
      key: "type",
      header: "Type",
      className: "w-24",
      render: (row) => <StatusBadge variant={TYPE_MAP[row.type] || "draft"} label={row.type} />,
    },
    {
      key: "title",
      header: "Title",
      render: (row) => (
        <div>
          <p className="text-sm font-medium text-gray-900">{row.title}</p>
          <p className="text-xs text-gray-500 mt-0.5 truncate max-w-md">{row.description}</p>
        </div>
      ),
    },
    {
      key: "metrics",
      header: "Metrics",
      render: (row) => (
        <div className="flex flex-wrap gap-2">
          {Object.entries(row.metrics).map(([key, val]) => (
            <span key={key} className="text-xs text-gray-500">
              <span className="font-medium text-gray-700">{formatNumber(val)}</span> {key.replace(/_/g, " ")}
            </span>
          ))}
        </div>
      ),
    },
    {
      key: "date",
      header: "Date",
      render: (row) => <span className="text-sm text-gray-500">{new Date(row.created_at).toLocaleDateString()}</span>,
    },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Queries Run" value={17} icon={Search} />
          <MetricCard label="Results Found" value={results.length} icon={Hash} />
          <MetricCard label="Regions Covered" value={8} icon={Globe} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Research tip" description="Combine keyword + region filters for the most relevant results in target markets." />
          <InsightItem title="API quota" description="17 of 100 daily queries used. Quota resets at midnight UTC." variant="default" />
        </InsightPanel>
      }
    >
      {/* Query Builder */}
      <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-5 mb-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Research Query Builder</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Keyword</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input type="text" value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="Search keyword..." className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Hashtag</label>
            <div className="relative">
              <Hash className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input type="text" value={hashtag} onChange={(e) => setHashtag(e.target.value)} placeholder="#hashtag" className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Username</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="@username" className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Region</label>
            <div className="relative">
              <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <select value={region} onChange={(e) => setRegion(e.target.value)} className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm appearance-none focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none">
                {REGIONS.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Date From</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Date To</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={handleSearch} disabled={searching || (!keyword.trim() && !hashtag.trim() && !username.trim())} className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 disabled:opacity-50 transition-colors">
            {searching ? "Searching..." : "Search"}
          </button>
          <button onClick={handleClear} className="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
            Clear
          </button>
        </div>
      </div>

      {hasSearched ? (
        <DataTable
          columns={columns}
          data={results}
          keyExtractor={(row) => row.id}
          emptyTitle="No results found"
          emptyDescription="Try adjusting your search criteria"
        />
      ) : (
        <div className="rounded-xl border border-gray-100 bg-white py-12 text-center">
          <Search className="h-8 w-8 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-500">Enter a keyword, hashtag, or username to query the TikTok Research API</p>
          <p className="text-xs text-gray-400 mt-1">Results will appear here after searching</p>
        </div>
      )}
    </PageShell>
  );
}
