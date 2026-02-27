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
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { Skeleton } from "@/components/ui/skeleton";
import { useWorkspace } from "@/hooks/useWorkspace";


const MODULE_CARDS = [
  {
    title: "Commerce",
    description: "Orders, products, revenue, and fulfillment metrics.",
    icon: ShoppingBag,
    href: "/analytics/commerce",
    gradient: "from-emerald-50 to-emerald-50/50",
    iconBg: "bg-emerald-100",
    iconColor: "text-emerald-600",
  },
  {
    title: "Advertising",
    description: "Campaign performance, spend, ROAS, and conversions.",
    icon: Megaphone,
    href: "/analytics/advertising",
    gradient: "from-purple/5 to-purple/[0.02]",
    iconBg: "bg-purple/10",
    iconColor: "text-purple",
  },
  {
    title: "Content",
    description: "Video performance, views, engagement, and trending content.",
    icon: Video,
    href: "/analytics/content",
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

function formatKpi(val: number | undefined | null): string {
  if (val === undefined || val === null) return "\u2014";
  if (val >= 1_000_000) return `${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `${(val / 1_000).toFixed(1)}K`;
  return val.toLocaleString();
}

export default function AnalyticsDashboardPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const [kpi, setKpi] = useState<KpiOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAccessToken();
    if (!token || !WORKSPACE_ID) {
      setLoading(false);
      return;
    }
    getKpiOverview(WORKSPACE_ID, token)
      .then(setKpi)
      .catch(() => setKpi(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <PageShell
      header={
        <MetricBar>
          {loading ? (
            <>
              <Skeleton className="h-16 flex-1 rounded-xl" />
              <Skeleton className="h-16 flex-1 rounded-xl" />
              <Skeleton className="h-16 flex-1 rounded-xl" />
              <Skeleton className="h-16 flex-1 rounded-xl" />
              <Skeleton className="h-16 flex-1 rounded-xl" />
            </>
          ) : (
            <>
              <MetricCard label="Total Orders" value={formatKpi(kpi?.total_orders)} icon={ShoppingCart} />
              <MetricCard label="Active Campaigns" value={formatKpi(kpi?.active_campaigns)} icon={Megaphone} />
              <MetricCard label="Total Videos" value={formatKpi(kpi?.total_videos)} icon={Play} />
              <MetricCard label="Total Views" value={formatKpi(kpi?.total_views)} icon={Eye} />
              <MetricCard label="Saved Creators" value={formatKpi(kpi?.saved_creators)} icon={Users} />
            </>
          )}
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem
            title="Unified overview"
            description="Cross-module KPIs aggregated from Commerce, Advertising, Content, and Creators."
            variant="success"
          />
          <InsightItem
            title="Drill down"
            description="Click any module card below to see detailed analytics with charts and top performers."
          />
        </InsightPanel>
      }
    >
      {/* Timeseries Placeholder */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="h-4 w-4 text-coral" />
          <h2 className="text-sm font-semibold text-gray-900">Performance Over Time</h2>
        </div>
        <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)]">
          <div className="flex flex-col items-center justify-center py-16 px-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-50 mb-3">
              <BarChart3 className="h-5 w-5 text-gray-300" />
            </div>
            <p className="text-sm text-gray-400">Timeseries chart coming soon</p>
            <p className="text-xs text-gray-300 mt-1">Visualize orders, revenue, views, and spend over time</p>
          </div>
        </div>
      </div>

      {/* Module Breakdown */}
      <div>
        <h2 className="text-sm font-semibold text-gray-900 mb-4">Module Breakdown</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {MODULE_CARDS.map((mod) => {
            const Icon = mod.icon;
            return (
              <Link
                key={mod.title}
                href={mod.href}
                className="group relative overflow-hidden rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-5 hover:shadow-md hover:border-gray-200 transition-all duration-200"
              >
                <div className={cn("absolute inset-0 bg-gradient-to-br opacity-50", mod.gradient)} />
                <div className="relative">
                  <div className="flex items-center gap-3 mb-2">
                    <div className={cn("flex h-9 w-9 items-center justify-center rounded-lg", mod.iconBg)}>
                      <Icon className={cn("h-[18px] w-[18px]", mod.iconColor)} />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-900 group-hover:text-gray-700 transition-colors">
                      {mod.title}
                    </h3>
                    <ArrowRight className="ml-auto h-4 w-4 text-gray-300 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200" />
                  </div>
                  <p className="text-xs text-gray-500 leading-relaxed">{mod.description}</p>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </PageShell>
  );
}
