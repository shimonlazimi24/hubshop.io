"use client";

import { useState } from "react";
import { Search, Hash, User, Globe, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";

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
  {
    id: "r1",
    type: "video",
    title: "Product Review: New Gadget 2026",
    description: "Unboxing and first impressions of the latest tech gadget trending on TikTok.",
    metrics: { views: 1_240_000, likes: 89_000, comments: 3_200, shares: 12_400 },
    created_at: "2026-02-18T14:00:00Z",
  },
  {
    id: "r2",
    type: "hashtag",
    title: "#SpringFashion2026",
    description: "Trending fashion hashtag with 52M+ views in the last 7 days.",
    metrics: { views: 52_000_000, videos: 34_000 },
    created_at: "2026-02-15T00:00:00Z",
  },
  {
    id: "r3",
    type: "user",
    title: "@trendsetter_official",
    description: "Fashion influencer with 1.2M followers, high engagement in beauty niche.",
    metrics: { followers: 1_200_000, videos: 342, avg_views: 280_000 },
    created_at: "2026-02-10T00:00:00Z",
  },
  {
    id: "r4",
    type: "video",
    title: "Easy Recipe: 5-Minute Pasta",
    description: "Quick cooking tutorial that went viral with 3M views in 24 hours.",
    metrics: { views: 3_400_000, likes: 234_000, comments: 8_900, shares: 45_000 },
    created_at: "2026-02-17T09:00:00Z",
  },
  {
    id: "r5",
    type: "hashtag",
    title: "#TikTokShopFinds",
    description: "Commerce-focused hashtag showing strong growth in SEA markets.",
    metrics: { views: 128_000_000, videos: 87_000 },
    created_at: "2026-02-12T00:00:00Z",
  },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

const TYPE_ICONS = {
  video: Search,
  user: User,
  hashtag: Hash,
};

const TYPE_COLORS = {
  video: "bg-blue-100 text-blue-800",
  user: "bg-green-100 text-green-800",
  hashtag: "bg-purple-100 text-purple-800",
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
    // Simulate API call with mock data
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

  return (
    <div className="max-w-6xl">
      {/* Query Builder */}
      <div className="rounded-xl border border-gray-100 bg-white p-5 mb-6">
        <h3 className="text-sm font-medium text-gray-900 mb-4">Research Query Builder</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Keyword</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="Search keyword..."
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Hashtag</label>
            <div className="relative">
              <Hash className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={hashtag}
                onChange={(e) => setHashtag(e.target.value)}
                placeholder="#hashtag"
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Username</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="@username"
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Region</label>
            <div className="relative">
              <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm appearance-none"
              >
                {REGIONS.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Date From</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Date To</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm"
              />
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleSearch}
            disabled={searching || (!keyword.trim() && !hashtag.trim() && !username.trim())}
            className="rounded-lg bg-coral px-4 py-2 text-sm font-medium text-white hover:bg-coral/90 disabled:opacity-50 transition-colors"
          >
            {searching ? "Searching..." : "Search"}
          </button>
          <button
            onClick={handleClear}
            className="px-4 py-2 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Results Table */}
      {hasSearched && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-4 py-3 border-b border-gray-200">
            <p className="text-sm text-gray-500">
              {results.length} result{results.length !== 1 ? "s" : ""} found
            </p>
          </div>
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 text-left">
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Title</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Metrics</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {results.map((result) => {
                const TypeIcon = TYPE_ICONS[result.type];
                return (
                  <tr key={result.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <span className={cn("inline-flex items-center gap-1 px-2 py-1 text-xs rounded-full", TYPE_COLORS[result.type])}>
                        <TypeIcon className="h-3 w-3" />
                        {result.type}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-sm font-medium text-gray-900">{result.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5 truncate max-w-md">{result.description}</p>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(result.metrics).map(([key, val]) => (
                          <span key={key} className="text-xs text-gray-500">
                            <span className="font-medium text-gray-700">{formatNumber(val)}</span> {key.replace(/_/g, " ")}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(result.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {results.length === 0 && (
            <div className="px-4 py-8 text-center text-gray-500">
              No results found. Try adjusting your search criteria.
            </div>
          )}
        </div>
      )}

      {!hasSearched && (
        <div className="rounded-xl border border-gray-100 bg-white py-12 text-center">
          <Search className="h-8 w-8 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-500">Enter a keyword, hashtag, or username to query the TikTok Research API</p>
          <p className="text-xs text-gray-400 mt-1">Results will appear here after searching</p>
        </div>
      )}
    </div>
  );
}
