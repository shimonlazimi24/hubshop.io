"use client";

import { useState } from "react";
import { Search, Users, TrendingUp, Filter } from "lucide-react";
import { cn } from "@/lib/utils";

interface ScoutedCreator {
  id: string;
  username: string;
  display_name: string;
  niche: string;
  follower_count: number;
  engagement_rate: number;
  avg_views: number;
}

const NICHE_OPTIONS = [
  { value: "", label: "All Niches" },
  { value: "beauty", label: "Beauty" },
  { value: "fashion", label: "Fashion" },
  { value: "food", label: "Food & Cooking" },
  { value: "fitness", label: "Fitness" },
  { value: "tech", label: "Tech" },
  { value: "comedy", label: "Comedy" },
  { value: "education", label: "Education" },
  { value: "lifestyle", label: "Lifestyle" },
];

const FOLLOWER_OPTIONS = [
  { value: "", label: "Any Followers" },
  { value: "nano", label: "Nano (1K-10K)" },
  { value: "micro", label: "Micro (10K-100K)" },
  { value: "mid", label: "Mid (100K-500K)" },
  { value: "macro", label: "Macro (500K-1M)" },
  { value: "mega", label: "Mega (1M+)" },
];

const ENGAGEMENT_OPTIONS = [
  { value: "", label: "Any Engagement" },
  { value: "1", label: "1%+" },
  { value: "3", label: "3%+" },
  { value: "5", label: "5%+" },
  { value: "10", label: "10%+" },
];

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

const NICHE_COLORS: Record<string, string> = {
  Beauty: "bg-pink-100 text-pink-800",
  Fashion: "bg-purple-100 text-purple-800",
  "Food & Cooking": "bg-orange-100 text-orange-800",
  Fitness: "bg-green-100 text-green-800",
  Tech: "bg-blue-100 text-blue-800",
  Comedy: "bg-yellow-100 text-yellow-800",
  Education: "bg-indigo-100 text-indigo-800",
  Lifestyle: "bg-gray-100 text-gray-800",
};

export default function CreatorScoutPage() {
  const [query, setQuery] = useState("");
  const [niche, setNiche] = useState("");
  const [followers, setFollowers] = useState("");
  const [engagement, setEngagement] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  const filteredCreators = MOCK_CREATORS.filter((c) => {
    if (query && !c.display_name.toLowerCase().includes(query.toLowerCase()) && !c.username.toLowerCase().includes(query.toLowerCase())) {
      return false;
    }
    if (niche && c.niche.toLowerCase() !== niche) return false;
    if (engagement && c.engagement_rate < Number(engagement)) return false;
    return true;
  });

  return (
    <div className="max-w-6xl">
      {/* Search Bar */}
      <div className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search creators by name or username..."
            className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm"
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={cn(
            "flex items-center gap-1.5 px-3 py-2 border rounded-md text-sm font-medium transition-colors",
            showFilters
              ? "border-coral text-coral bg-coral/5"
              : "border-gray-300 text-gray-600 hover:bg-gray-50"
          )}
        >
          <Filter className="h-4 w-4" />
          Filters
        </button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="rounded-xl border border-gray-100 bg-white p-4 mb-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Niche</label>
              <select
                value={niche}
                onChange={(e) => setNiche(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                {NICHE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Followers</label>
              <select
                value={followers}
                onChange={(e) => setFollowers(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                {FOLLOWER_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 uppercase mb-1">Min Engagement</label>
              <select
                value={engagement}
                onChange={(e) => setEngagement(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                {ENGAGEMENT_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Results Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredCreators.map((creator) => (
          <div
            key={creator.id}
            className="rounded-xl border border-gray-100 bg-white p-5 hover:shadow-md hover:border-gray-200 transition-all duration-200"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 text-sm font-medium">
                {creator.display_name[0]}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{creator.display_name}</p>
                <p className="text-xs text-gray-500">@{creator.username}</p>
              </div>
            </div>

            <span className={cn("inline-block px-2 py-0.5 text-xs rounded-full mb-3", NICHE_COLORS[creator.niche] || "bg-gray-100 text-gray-800")}>
              {creator.niche}
            </span>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  <Users className="h-3.5 w-3.5 text-gray-400" />
                  <span className="text-xs text-gray-500">Followers</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{formatNumber(creator.follower_count)}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  <TrendingUp className="h-3.5 w-3.5 text-gray-400" />
                  <span className="text-xs text-gray-500">Engagement</span>
                </div>
                <span className="text-sm font-medium text-green-600">{creator.engagement_rate}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">Avg. Views</span>
                <span className="text-sm font-medium text-gray-900">{formatNumber(creator.avg_views)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredCreators.length === 0 && (
        <div className="rounded-xl border border-gray-100 bg-white py-12 text-center">
          <Users className="h-8 w-8 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-500">No creators match your search criteria</p>
        </div>
      )}
    </div>
  );
}
