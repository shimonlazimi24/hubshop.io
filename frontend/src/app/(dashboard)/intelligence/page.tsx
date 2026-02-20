"use client";

import { useState } from "react";
import Link from "next/link";
import {
  TrendingUp,
  Eye,
  Users,
  Search,
  ArrowRight,
  Hash,
} from "lucide-react";
import { cn } from "@/lib/utils";

const KPI_CARDS = [
  {
    label: "Trending Hashtags",
    value: 142,
    icon: Hash,
    color: "text-purple bg-purple/5 border-purple/10",
    iconColor: "text-purple",
  },
  {
    label: "Tracked Competitors",
    value: 8,
    icon: Eye,
    color: "text-emerald-600 bg-emerald-50 border-emerald-100",
    iconColor: "text-emerald-500",
  },
  {
    label: "Scouted Creators",
    value: 34,
    icon: Users,
    color: "text-coral bg-coral/5 border-coral/10",
    iconColor: "text-coral",
  },
  {
    label: "Research Queries",
    value: 17,
    icon: Search,
    color: "text-blue-600 bg-blue-50 border-blue-100",
    iconColor: "text-blue-500",
  },
];

const QUICK_LINKS = [
  {
    title: "Trends",
    description: "Discover trending hashtags, sounds, and products across regions.",
    icon: TrendingUp,
    href: "/intelligence/trends",
    gradient: "from-purple/5 to-purple/[0.02]",
    iconBg: "bg-purple/10",
    iconColor: "text-purple",
  },
  {
    title: "Competitors",
    description: "Track competitor accounts, content, and engagement metrics.",
    icon: Eye,
    href: "/intelligence/competitors",
    gradient: "from-emerald-50 to-emerald-50/50",
    iconBg: "bg-emerald-100",
    iconColor: "text-emerald-600",
  },
  {
    title: "Creator Scout",
    description: "Find and evaluate creators by niche, followers, and engagement.",
    icon: Users,
    href: "/intelligence/creators",
    gradient: "from-coral/10 to-coral/5",
    iconBg: "bg-coral/10",
    iconColor: "text-coral",
  },
  {
    title: "Research API",
    description: "Query the TikTok Research API for hashtags, users, and videos.",
    icon: Search,
    href: "/intelligence/research",
    gradient: "from-blue-50 to-blue-50/50",
    iconBg: "bg-blue-100",
    iconColor: "text-blue-600",
  },
];

export default function IntelligenceOverviewPage() {
  const [loading] = useState(false);

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
              {loading ? (
                <div className="h-8 w-16 mb-2 rounded bg-gray-100 animate-pulse" />
              ) : (
                <p className="text-2xl font-semibold text-gray-900">
                  {card.value.toLocaleString()}
                </p>
              )}
              <p className="text-xs text-gray-400 mt-1">{card.label}</p>
            </div>
          );
        })}
      </div>

      {/* Quick Links */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Intelligence Modules
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {QUICK_LINKS.map((mod) => {
            const Icon = mod.icon;
            return (
              <Link
                key={mod.title}
                href={mod.href}
                className="group relative overflow-hidden rounded-xl border border-gray-100 bg-white p-5 hover:shadow-md hover:border-gray-200 transition-all duration-200"
              >
                <div
                  className={cn(
                    "absolute inset-0 bg-gradient-to-br opacity-50",
                    mod.gradient
                  )}
                />
                <div className="relative">
                  <div className="flex items-center gap-3 mb-2">
                    <div
                      className={cn(
                        "flex h-9 w-9 items-center justify-center rounded-lg",
                        mod.iconBg
                      )}
                    >
                      <Icon
                        className={cn("h-[18px] w-[18px]", mod.iconColor)}
                      />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-900 group-hover:text-gray-700 transition-colors">
                      {mod.title}
                    </h3>
                    <ArrowRight className="ml-auto h-4 w-4 text-gray-300 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200" />
                  </div>
                  <p className="text-xs text-gray-500 leading-relaxed">
                    {mod.description}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
