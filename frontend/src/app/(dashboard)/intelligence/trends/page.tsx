"use client";

import { useState } from "react";
import { Hash, Music, ShoppingBag, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

type TrendTab = "hashtags" | "sounds" | "products";

const TABS: { key: TrendTab; label: string; icon: typeof Hash }[] = [
  { key: "hashtags", label: "Hashtags", icon: Hash },
  { key: "sounds", label: "Sounds", icon: Music },
  { key: "products", label: "Products", icon: ShoppingBag },
];

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

const MOCK_HASHTAGS = [
  { rank: 1, name: "#TikTokMadeMeBuyIt", views: 52_400_000_000, growth: 12.4 },
  { rank: 2, name: "#GRWM", views: 41_200_000_000, growth: 8.7 },
  { rank: 3, name: "#SmallBusiness", views: 38_900_000_000, growth: 15.2 },
  { rank: 4, name: "#BookTok", views: 34_100_000_000, growth: 6.1 },
  { rank: 5, name: "#FYP", views: 29_800_000_000, growth: -2.3 },
  { rank: 6, name: "#LifeHack", views: 27_500_000_000, growth: 9.8 },
  { rank: 7, name: "#OOTD", views: 24_300_000_000, growth: 4.5 },
  { rank: 8, name: "#Recipe", views: 21_700_000_000, growth: 11.3 },
];

const MOCK_SOUNDS = [
  { rank: 1, name: "Original Sound - @creator1", uses: 2_340_000, growth: 45.2 },
  { rank: 2, name: "Trending Beat #42", uses: 1_890_000, growth: 32.1 },
  { rank: 3, name: "Viral Audio Clip", uses: 1_560_000, growth: 28.7 },
  { rank: 4, name: "Popular Song Remix", uses: 1_230_000, growth: 15.4 },
  { rank: 5, name: "Comedy Skit Sound", uses: 980_000, growth: 22.3 },
  { rank: 6, name: "Dance Challenge Beat", uses: 870_000, growth: 19.8 },
];

const MOCK_PRODUCTS = [
  { rank: 1, name: "LED Strip Lights", orders: 145_000, growth: 34.5 },
  { rank: 2, name: "Portable Blender", orders: 128_000, growth: 28.9 },
  { rank: 3, name: "Phone Ring Light", orders: 112_000, growth: 21.3 },
  { rank: 4, name: "Skincare Serum Set", orders: 98_000, growth: 18.7 },
  { rank: 5, name: "Wireless Earbuds", orders: 87_000, growth: 12.4 },
  { rank: 6, name: "Mini Projector", orders: 76_000, growth: 25.6 },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)}B`;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export default function TrendsPage() {
  const [tab, setTab] = useState<TrendTab>("hashtags");
  const [region, setRegion] = useState("");

  return (
    <div className="max-w-6xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex gap-2">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors",
                tab === t.key
                  ? "bg-gray-900 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              )}
            >
              <t.icon className="h-3.5 w-3.5" />
              {t.label}
            </button>
          ))}
        </div>
        <select
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm"
        >
          {REGIONS.map((r) => (
            <option key={r.value} value={r.value}>
              {r.label}
            </option>
          ))}
        </select>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase w-16">Rank</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">
                {tab === "hashtags" ? "Hashtag" : tab === "sounds" ? "Sound" : "Product"}
              </th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">
                {tab === "hashtags" ? "Views" : tab === "sounds" ? "Uses" : "Orders"}
              </th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Growth</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {tab === "hashtags" &&
              MOCK_HASHTAGS.map((item) => (
                <tr key={item.rank} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-gray-100 text-xs font-semibold text-gray-700">
                      {item.rank}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Hash className="h-4 w-4 text-purple" />
                      <span className="text-sm font-medium text-gray-900">{item.name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {formatNumber(item.views)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <TrendingUp className={cn("h-3.5 w-3.5", item.growth >= 0 ? "text-green-500" : "text-red-500")} />
                      <span className={cn("text-sm font-medium", item.growth >= 0 ? "text-green-600" : "text-red-600")}>
                        {item.growth >= 0 ? "+" : ""}{item.growth}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}

            {tab === "sounds" &&
              MOCK_SOUNDS.map((item) => (
                <tr key={item.rank} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-gray-100 text-xs font-semibold text-gray-700">
                      {item.rank}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Music className="h-4 w-4 text-cyan" />
                      <span className="text-sm font-medium text-gray-900">{item.name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {formatNumber(item.uses)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <TrendingUp className="h-3.5 w-3.5 text-green-500" />
                      <span className="text-sm font-medium text-green-600">
                        +{item.growth}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}

            {tab === "products" &&
              MOCK_PRODUCTS.map((item) => (
                <tr key={item.rank} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-gray-100 text-xs font-semibold text-gray-700">
                      {item.rank}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <ShoppingBag className="h-4 w-4 text-emerald-500" />
                      <span className="text-sm font-medium text-gray-900">{item.name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {formatNumber(item.orders)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <TrendingUp className="h-3.5 w-3.5 text-green-500" />
                      <span className="text-sm font-medium text-green-600">
                        +{item.growth}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
