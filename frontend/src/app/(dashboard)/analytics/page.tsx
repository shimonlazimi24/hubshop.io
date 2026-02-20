"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShoppingCart,
  Megaphone,
  Play,
  Eye,
  Users,
  ShoppingBag,
  BarChart3,
  Video,
  Star,
  ArrowRight,
} from "lucide-react";
import { getAccessToken } from "@/lib/auth";
import { getKpiOverview, type KpiOverview } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const MODULE_CARDS = [
  {
    title: "Commerce",
    description: "Orders, products, revenue, and fulfillment metrics.",
    icon: ShoppingBag,
    href: "/commerce",
    gradient: "from-emerald-50 to-emerald-50/50",
    iconBg: "bg-emerald-100",
    iconColor: "text-emerald-600",
  },
  {
    title: "Advertising",
    description: "Campaign performance, spend, ROAS, and conversions.",
    icon: Megaphone,
    href: "/ads",
    gradient: "from-purple/5 to-purple/[0.02]",
    iconBg: "bg-purple/10",
    iconColor: "text-purple",
  },
  {
    title: "Content",
    description: "Video performance, views, engagement, and trending content.",
    icon: Video,
    href: "/content",
    gradient: "from-cyan/5 to-cyan/[0.02]",
    iconBg: "bg-cyan/10",
    iconColor: "text-cyan",
  },
  {
    title: "Creators",
    description: "Creator partnerships, affiliate performance, and collaborations.",
    icon: Star,
    href: "/creators",
    gradient: "from-coral/10 to-coral/5",
    iconBg: "bg-coral/10",
    iconColor: "text-coral",
  },
];

export default function AnalyticsDashboardPage() {
  const [kpi, setKpi] = useState<KpiOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }
    getKpiOverview(WORKSPACE_ID, token)
      .then(setKpi)
      .catch(() => setKpi(null))
      .finally(() => setLoading(false));
  }, []);

  const kpiCards = [
    {
      label: "Total Orders",
      value: kpi?.total_orders,
      icon: ShoppingCart,
      color: "text-emerald-600 bg-emerald-50 border-emerald-100",
      iconColor: "text-emerald-500",
    },
    {
      label: "Active Campaigns",
      value: kpi?.active_campaigns,
      icon: Megaphone,
      color: "text-purple bg-purple/5 border-purple/10",
      iconColor: "text-purple",
    },
    {
      label: "Total Videos",
      value: kpi?.total_videos,
      icon: Play,
      color: "text-cyan bg-cyan/5 border-cyan/10",
      iconColor: "text-cyan",
    },
    {
      label: "Total Views",
      value: kpi?.total_views,
      icon: Eye,
      color: "text-blue-600 bg-blue-50 border-blue-100",
      iconColor: "text-blue-500",
    },
    {
      label: "Saved Creators",
      value: kpi?.saved_creators,
      icon: Users,
      color: "text-coral bg-coral/5 border-coral/10",
      iconColor: "text-coral",
    },
  ];

  return (
    <div className="max-w-6xl">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {kpiCards.map((card) => {
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
                <Skeleton className="h-8 w-16 mb-2" />
              ) : (
                <p className="text-2xl font-semibold text-gray-900">
                  {card.value !== undefined && card.value !== null
                    ? card.value.toLocaleString()
                    : "\u2014"}
                </p>
              )}
              <p className="text-xs text-gray-400 mt-1">{card.label}</p>
            </div>
          );
        })}
      </div>

      {/* Timeseries Placeholder */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="h-4 w-4 text-coral" />
          <h2 className="text-sm font-semibold text-gray-900">
            Performance Over Time
          </h2>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white">
          <div className="flex flex-col items-center justify-center py-16 px-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-50 mb-3">
              <BarChart3 className="h-5 w-5 text-gray-300" />
            </div>
            <p className="text-sm text-gray-400">
              Timeseries chart coming soon
            </p>
            <p className="text-xs text-gray-300 mt-1">
              Visualize orders, revenue, views, and spend over time
            </p>
          </div>
        </div>
      </div>

      {/* Module Breakdown */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Module Breakdown
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {MODULE_CARDS.map((mod) => {
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
