"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Eye,
  AtSign,
  Users,
  TrendingUp,
  ArrowRight,
  Upload,
} from "lucide-react";
import { cn } from "@/lib/utils";

const KPI_CARDS = [
  {
    label: "Post Reach",
    value: "1.2M",
    icon: Eye,
    color: "text-purple bg-purple/5 border-purple/10",
    iconColor: "text-purple",
  },
  {
    label: "Brand Mentions",
    value: 342,
    icon: AtSign,
    color: "text-coral bg-coral/5 border-coral/10",
    iconColor: "text-coral",
  },
  {
    label: "Followers",
    value: "48.2K",
    icon: Users,
    color: "text-emerald-600 bg-emerald-50 border-emerald-100",
    iconColor: "text-emerald-500",
  },
  {
    label: "Engagement Rate",
    value: "5.8%",
    icon: TrendingUp,
    color: "text-blue-600 bg-blue-50 border-blue-100",
    iconColor: "text-blue-500",
  },
];

const QUICK_LINKS = [
  {
    title: "Mentions",
    description: "Track brand mentions, popular hashtags, and user sentiment.",
    icon: AtSign,
    href: "/organic/mentions",
    gradient: "from-coral/10 to-coral/5",
    iconBg: "bg-coral/10",
    iconColor: "text-coral",
  },
  {
    title: "Publish",
    description: "Create and schedule organic posts with hashtag recommendations.",
    icon: Upload,
    href: "/organic/publish",
    gradient: "from-emerald-50 to-emerald-50/50",
    iconBg: "bg-emerald-100",
    iconColor: "text-emerald-600",
  },
];

export default function OrganicOverviewPage() {
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
                  {typeof card.value === "number"
                    ? card.value.toLocaleString()
                    : card.value}
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
          Organic Modules
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
