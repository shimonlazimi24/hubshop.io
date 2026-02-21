"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  DollarSign,
  Megaphone,
  Eye,
  Users,
  TrendingUp,
  ShoppingCart,
  Film,
  MessageSquare,
  Brain,
  AlertTriangle,
  CheckCircle,
  Clock,
  ArrowRight,
  RefreshCw,
  Lightbulb,
  Package,
  Radio,
  Plus,
  Upload,
  Zap,
} from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { getAccessToken } from "@/lib/auth";
import { getKpiOverview, type KpiOverview } from "@/lib/api";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const ACTION_ITEMS = [
  {
    label: "3 campaigns need attention",
    description: "Budget pacing is off for 3 active campaigns",
    href: "/ads",
    variant: "warning" as const,
    icon: Megaphone,
  },
  {
    label: "5 pending orders",
    description: "Orders awaiting shipment past SLA",
    href: "/commerce",
    variant: "danger" as const,
    icon: ShoppingCart,
  },
  {
    label: "2 creatives fatigued",
    description: "Creative fatigue detected — refresh recommended",
    href: "/creatives",
    variant: "warning" as const,
    icon: Film,
  },
];

const MODULE_HEALTH = [
  {
    name: "Commerce",
    icon: ShoppingCart,
    health: "green" as const,
    metric: "142 orders today",
    href: "/commerce",
  },
  {
    name: "Ads",
    icon: Megaphone,
    health: "yellow" as const,
    metric: "3.2x ROAS",
    href: "/ads",
  },
  {
    name: "Content",
    icon: Film,
    health: "green" as const,
    metric: "1.2M views this week",
    href: "/content",
  },
  {
    name: "Creators",
    icon: Users,
    health: "green" as const,
    metric: "24 active partnerships",
    href: "/creators",
  },
  {
    name: "Messaging",
    icon: MessageSquare,
    health: "yellow" as const,
    metric: "12 min avg response",
    href: "/messaging",
  },
  {
    name: "Intelligence",
    icon: Brain,
    health: "green" as const,
    metric: "8 trends tracked",
    href: "/intelligence",
  },
];

const HEALTH_COLORS: Record<string, string> = {
  green: "bg-success",
  yellow: "bg-warning",
  red: "bg-danger",
};

const RECENT_ACTIVITY = [
  { text: "Order #TT-8842 shipped via FedEx", time: "12 min ago", icon: Package },
  { text: "Campaign 'Summer Sale' budget increased 20%", time: "1h ago", icon: Megaphone },
  { text: "New video published: 'Product Showcase Q1'", time: "2h ago", icon: Film },
  { text: "Spark Ad authorization approved for @creator_jane", time: "3h ago", icon: CheckCircle },
  { text: "Daily KPI snapshot completed", time: "6h ago", icon: TrendingUp },
  { text: "LIVE session ended: 2.4K peak viewers", time: "8h ago", icon: Radio },
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

  return (
    <div>
      <PageHeader
        title="Overview"
        description="Your unified TikTok command center"
      />

      <PageShell
        header={
          <MetricBar className="grid-cols-2 sm:grid-cols-3 lg:grid-cols-5">
            <MetricCard
              label="Revenue"
              value={loading ? "..." : "$48.2K"}
              icon={DollarSign}
              iconColor="text-success"
              trend={{ value: 12.5, direction: "up", label: "vs last week" }}
              sparklineData={[32, 35, 40, 38, 42, 45, 48]}
              loading={loading}
            />
            <MetricCard
              label="Ad Spend"
              value={loading ? "..." : "$12.4K"}
              icon={Megaphone}
              iconColor="text-purple"
              trend={{ value: 8.2, direction: "up", label: "vs last week" }}
              sparklineData={[10, 11, 10.5, 12, 11.8, 12.2, 12.4]}
              loading={loading}
            />
            <MetricCard
              label="ROAS"
              value={loading ? "..." : "3.2x"}
              icon={TrendingUp}
              iconColor="text-coral"
              trend={{ value: 5.1, direction: "up", label: "vs last week" }}
              sparklineData={[2.8, 2.9, 3.0, 3.1, 3.0, 3.15, 3.2]}
              loading={loading}
            />
            <MetricCard
              label="Content Views"
              value={loading ? "..." : kpi ? kpi.total_videos.toLocaleString() : "1.2M"}
              icon={Eye}
              iconColor="text-cyan"
              trend={{ value: 18.3, direction: "up", label: "vs last week" }}
              sparklineData={[800, 850, 900, 950, 1000, 1100, 1200]}
              loading={loading}
            />
            <MetricCard
              label="Followers"
              value={loading ? "..." : "84.5K"}
              icon={Users}
              iconColor="text-info"
              trend={{ value: 2.1, direction: "up", label: "vs last week" }}
              sparklineData={[80, 81, 82, 82.5, 83, 83.8, 84.5]}
              loading={loading}
            />
          </MetricBar>
        }
        aside={
          <InsightPanel defaultOpen={false}>
            <InsightItem
              icon={<Lightbulb className="h-4 w-4 text-coral" />}
              title="Top recommendation"
              description="Increase budget on 'Summer Sale' campaign — it has the highest ROAS at 4.8x"
              variant="success"
              action={{ label: "View campaign", onClick: () => {} }}
            />
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-info" />}
              title="Trending alert"
              description="'DIY crafts' is trending in your category. Consider creating related content."
              variant="default"
              action={{ label: "See trends", onClick: () => {} }}
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="SLA warning"
              description="5 orders are approaching their ship-by deadline. Fulfill within 4 hours."
              variant="warning"
              action={{ label: "View orders", onClick: () => {} }}
            />
          </InsightPanel>
        }
      >
        {/* Quick Actions */}
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Zap className="h-4 w-4 text-coral" />
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <Link
              href="/ads/campaigns/new"
              className="group flex items-center gap-3 rounded-xl border border-coral/20 bg-coral/5 p-4 hover:bg-coral/10 hover:shadow-[var(--shadow-panel)] transition-all duration-[var(--duration-fast)]"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-coral text-white shadow-sm">
                <Plus className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-900">Launch Campaign</p>
                <p className="text-xs text-gray-500">Create a new TikTok ad campaign</p>
              </div>
            </Link>
            <Link
              href="/content/publish"
              className="group flex items-center gap-3 rounded-xl border border-info/20 bg-info/5 p-4 hover:bg-info/10 hover:shadow-[var(--shadow-panel)] transition-all duration-[var(--duration-fast)]"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-info text-white shadow-sm">
                <Upload className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-900">Publish Content</p>
                <p className="text-xs text-gray-500">Upload and schedule a new video</p>
              </div>
            </Link>
            <Link
              href="/creators/campaigns/new"
              className="group flex items-center gap-3 rounded-xl border border-purple/20 bg-purple/5 p-4 hover:bg-purple/10 hover:shadow-[var(--shadow-panel)] transition-all duration-[var(--duration-fast)]"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple text-white shadow-sm">
                <Users className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-900">Creator Campaign</p>
                <p className="text-xs text-gray-500">Launch a new influencer collaboration</p>
              </div>
            </Link>
          </div>
        </div>

        {/* Action Items */}
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-warning" />
            Action Items
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {ACTION_ITEMS.map((item) => {
              const Icon = item.icon;
              const borderColor =
                item.variant === "danger" ? "border-danger/20" : "border-warning/20";
              const bgColor =
                item.variant === "danger" ? "bg-danger/5" : "bg-warning/5";
              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={`group rounded-xl border ${borderColor} ${bgColor} p-4 hover:shadow-[var(--shadow-panel)] transition-all duration-[var(--duration-fast)]`}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white shadow-sm">
                      <Icon className="h-4 w-4 text-gray-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">{item.label}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{item.description}</p>
                    </div>
                    <ArrowRight className="h-4 w-4 text-gray-300 group-hover:text-gray-500 transition-colors flex-shrink-0 mt-0.5" />
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Module Health Grid */}
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-success" />
            Module Health
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {MODULE_HEALTH.map((mod) => {
              const Icon = mod.icon;
              return (
                <Link
                  key={mod.name}
                  href={mod.href}
                  className="group rounded-xl border border-gray-100 bg-white p-4 hover:shadow-[var(--shadow-panel)] transition-all duration-[var(--duration-fast)]"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`h-2 w-2 rounded-full ${HEALTH_COLORS[mod.health]}`} />
                    <Icon className="h-4 w-4 text-gray-400" />
                  </div>
                  <p className="text-sm font-semibold text-gray-900">{mod.name}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{mod.metric}</p>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Recent Activity Feed */}
        <div>
          <h2 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Clock className="h-4 w-4 text-gray-400" />
            Recent Activity
          </h2>
          <div className="rounded-xl border border-gray-100 bg-white divide-y divide-gray-50">
            {RECENT_ACTIVITY.map((event, i) => {
              const Icon = event.icon;
              return (
                <div key={i} className="flex items-center gap-3 px-4 py-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gray-50 flex-shrink-0">
                    <Icon className="h-4 w-4 text-gray-400" />
                  </div>
                  <p className="text-sm text-gray-700 flex-1">{event.text}</p>
                  <span className="text-xs text-gray-400 flex-shrink-0">{event.time}</span>
                </div>
              );
            })}
          </div>
        </div>
      </PageShell>
    </div>
  );
}
