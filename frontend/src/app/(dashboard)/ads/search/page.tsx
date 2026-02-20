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
} from "lucide-react";
import { cn } from "@/lib/utils";

const KPI_CARDS = [
  {
    label: "Keywords Tracked",
    value: 128,
    icon: Search,
    color: "text-purple bg-purple/5 border-purple/10",
    iconColor: "text-purple",
  },
  {
    label: "Negative Keywords",
    value: 34,
    icon: Ban,
    color: "text-coral bg-coral/5 border-coral/10",
    iconColor: "text-coral",
  },
  {
    label: "Avg Quality Score",
    value: "7.4",
    icon: Star,
    color: "text-emerald-600 bg-emerald-50 border-emerald-100",
    iconColor: "text-emerald-500",
  },
  {
    label: "Campaign Health",
    value: "92%",
    icon: HeartPulse,
    color: "text-blue-600 bg-blue-50 border-blue-100",
    iconColor: "text-blue-500",
  },
];

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

  return (
    <div className="max-w-6xl">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {KPI_CARDS.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.label}
              className="rounded-xl border border-gray-100 bg-white p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <div
                  className={cn(
                    "flex h-9 w-9 items-center justify-center rounded-lg",
                    card.color
                  )}
                >
                  <Icon className={cn("h-[18px] w-[18px]", card.iconColor)} />
                </div>
              </div>
              <p className="text-2xl font-semibold text-gray-900">
                {typeof card.value === "number"
                  ? card.value.toLocaleString()
                  : card.value}
              </p>
              <p className="text-xs text-gray-400 mt-1">{card.label}</p>
            </div>
          );
        })}
      </div>

      {/* Keyword Research Tool */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Keyword Research Tool
        </h2>
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
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm"
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
            <div className="bg-white rounded-lg border border-gray-200">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 text-left">
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Keyword</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Volume</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Competition</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">CPC</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Trend</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {MOCK_KEYWORD_RESULTS.map((kw) => (
                    <tr key={kw.keyword} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <span className="text-sm font-medium text-gray-900">{kw.keyword}</span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {formatNumber(kw.volume)}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={cn(
                            "px-2 py-0.5 text-xs rounded-full",
                            kw.competition === "High"
                              ? "bg-red-100 text-red-700"
                              : kw.competition === "Medium"
                              ? "bg-yellow-100 text-yellow-700"
                              : "bg-green-100 text-green-700"
                          )}
                        >
                          {kw.competition}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        ${kw.cpc.toFixed(2)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          {kw.trend >= 0 ? (
                            <TrendingUp className="h-3.5 w-3.5 text-green-500" />
                          ) : (
                            <TrendingDown className="h-3.5 w-3.5 text-red-500" />
                          )}
                          <span
                            className={cn(
                              "text-sm font-medium",
                              kw.trend >= 0 ? "text-green-600" : "text-red-600"
                            )}
                          >
                            {kw.trend >= 0 ? "+" : ""}{kw.trend}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Negative Keywords Management */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Negative Keywords
        </h2>
        <div className="rounded-xl border border-gray-100 bg-white p-5">
          <div className="flex gap-3 mb-4">
            <input
              type="text"
              value={newNegative}
              onChange={(e) => setNewNegative(e.target.value)}
              placeholder="Add a negative keyword"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
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
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-50 text-red-700 rounded-full text-sm"
              >
                <Ban className="h-3 w-3" />
                {nk.keyword}
                <button className="ml-0.5 hover:text-red-900">
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Campaign Health Cards */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Campaign Health
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {MOCK_CAMPAIGN_HEALTH.map((campaign) => (
            <div
              key={campaign.id}
              className="rounded-xl border border-gray-100 bg-white p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-gray-900">
                  {campaign.name}
                </h3>
                <span
                  className={cn(
                    "px-2 py-0.5 text-xs rounded-full font-medium",
                    campaign.status === "healthy"
                      ? "bg-green-100 text-green-700"
                      : campaign.status === "warning"
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-red-100 text-red-700"
                  )}
                >
                  {campaign.status === "healthy"
                    ? "Healthy"
                    : campaign.status === "warning"
                    ? "Warning"
                    : "Critical"}
                </span>
              </div>
              <div className="flex items-center gap-3 mb-2">
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={cn(
                      "h-full rounded-full transition-all",
                      campaign.score >= 80
                        ? "bg-green-500"
                        : campaign.score >= 60
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    )}
                    style={{ width: `${campaign.score}%` }}
                  />
                </div>
                <span className="text-sm font-semibold text-gray-900">
                  {campaign.score}
                </span>
              </div>
              {campaign.issues.length > 0 && (
                <ul className="mt-2 space-y-1">
                  {campaign.issues.map((issue, i) => (
                    <li
                      key={i}
                      className="text-xs text-gray-500 flex items-center gap-1.5"
                    >
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
    </div>
  );
}
