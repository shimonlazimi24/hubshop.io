"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Link2,
  ShoppingBag,
  Megaphone,
  Play,
  ArrowRight,
  ShoppingCart,
  Package,
  BarChart3,
  Zap,
} from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { cn } from "@/lib/utils";
import { getAccessToken } from "@/lib/auth";
import { getKpiOverview, type KpiOverview } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

interface KpiCard {
  label: string;
  value: string;
  hint: string;
  icon: typeof Link2;
  color: string;
  iconColor: string;
  href: string;
}

function buildKpiCards(kpi: KpiOverview | null, loading: boolean): KpiCard[] {
  return [
    {
      label: "Connected Accounts",
      value: "\u2014",
      hint: "Connect to see data",
      icon: Link2,
      color: "text-coral bg-coral/5 border-coral/10",
      iconColor: "text-coral",
      href: "/connect",
    },
    {
      label: "Total Orders",
      value: loading ? "..." : kpi ? kpi.total_orders.toLocaleString() : "\u2014",
      hint: kpi && kpi.total_orders > 0 ? "Across all shops" : "Sync your shop first",
      icon: ShoppingCart,
      color: "text-emerald-600 bg-emerald-50 border-emerald-100",
      iconColor: "text-emerald-500",
      href: "/commerce",
    },
    {
      label: "Active Campaigns",
      value: loading ? "..." : kpi ? kpi.active_campaigns.toLocaleString() : "\u2014",
      hint: kpi && kpi.active_campaigns > 0 ? "Currently running" : "Connect Ads account",
      icon: Megaphone,
      color: "text-purple bg-purple/5 border-purple/10",
      iconColor: "text-purple",
      href: "/ads",
    },
    {
      label: "Total Videos",
      value: loading ? "..." : kpi ? kpi.total_videos.toLocaleString() : "\u2014",
      hint: kpi && kpi.total_videos > 0 ? "Published content" : "Connect Developer account",
      icon: Play,
      color: "text-cyan bg-cyan/5 border-cyan/10",
      iconColor: "text-cyan",
      href: "/content",
    },
  ];
}

const QUICK_ACTIONS = [
  {
    title: "Connect TikTok Shop",
    description: "Link your seller account to manage commerce, orders, and inventory from one place.",
    icon: ShoppingBag,
    href: "/connect",
    gradient: "from-coral/10 to-coral/5",
    iconBg: "bg-coral/10",
    iconColor: "text-coral",
  },
  {
    title: "Browse Orders",
    description: "View and manage orders across all your connected shops with real-time updates.",
    icon: Package,
    href: "/commerce",
    gradient: "from-emerald-50 to-emerald-50/50",
    iconBg: "bg-emerald-100",
    iconColor: "text-emerald-600",
  },
  {
    title: "Launch Campaign",
    description: "Create and monitor TikTok ad campaigns, including GMV Max for shop promotion.",
    icon: Megaphone,
    href: "/ads",
    gradient: "from-purple/5 to-purple/[0.02]",
    iconBg: "bg-purple/10",
    iconColor: "text-purple",
  },
  {
    title: "View Analytics",
    description: "Cross-platform analytics bringing together commerce, ads, and content performance.",
    icon: BarChart3,
    href: "/analytics",
    gradient: "from-cyan/5 to-cyan/[0.02]",
    iconBg: "bg-cyan/10",
    iconColor: "text-cyan",
  },
];

export default function OverviewPage() {
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

  const kpiCards = buildKpiCards(kpi, loading);

  return (
    <div className="max-w-6xl">
      <PageHeader
        title="Overview"
        description="Your unified TikTok command center"
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {kpiCards.map((kpiCard) => {
          const Icon = kpiCard.icon;
          return (
            <Link
              key={kpiCard.label}
              href={kpiCard.href}
              className="group rounded-xl border border-gray-100 bg-white p-5 hover:shadow-md hover:border-gray-200 transition-all duration-200"
            >
              <div className="flex items-center justify-between mb-3">
                <div className={cn("flex h-9 w-9 items-center justify-center rounded-lg", kpiCard.color)}>
                  <Icon className={cn("h-[18px] w-[18px]", kpiCard.iconColor)} />
                </div>
                <ArrowRight className="h-4 w-4 text-gray-300 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200" />
              </div>
              {loading && kpiCard.label !== "Connected Accounts" ? (
                <Skeleton className="h-8 w-16 mb-2" />
              ) : (
                <p className="text-2xl font-semibold text-gray-900">{kpiCard.value}</p>
              )}
              <p className="text-xs text-gray-400 mt-1">{kpiCard.hint}</p>
            </Link>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="h-4 w-4 text-coral" />
          <h2 className="text-sm font-semibold text-gray-900">Quick Actions</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {QUICK_ACTIONS.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.title}
                href={action.href}
                className="group relative overflow-hidden rounded-xl border border-gray-100 bg-white p-5 hover:shadow-md hover:border-gray-200 transition-all duration-200"
              >
                {/* Subtle gradient background */}
                <div className={cn("absolute inset-0 bg-gradient-to-br opacity-50", action.gradient)} />
                <div className="relative">
                  <div className="flex items-center gap-3 mb-2">
                    <div className={cn("flex h-9 w-9 items-center justify-center rounded-lg", action.iconBg)}>
                      <Icon className={cn("h-[18px] w-[18px]", action.iconColor)} />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-900 group-hover:text-gray-700 transition-colors">
                      {action.title}
                    </h3>
                    <ArrowRight className="ml-auto h-4 w-4 text-gray-300 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200" />
                  </div>
                  <p className="text-xs text-gray-500 leading-relaxed">{action.description}</p>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-sm font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="rounded-xl border border-gray-100 bg-white">
          <div className="flex flex-col items-center justify-center py-12 px-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-50 mb-3">
              <Zap className="h-5 w-5 text-gray-300" />
            </div>
            <p className="text-sm text-gray-400">No recent activity</p>
            <p className="text-xs text-gray-300 mt-1">
              Events from orders, syncs, and campaigns will show here
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
