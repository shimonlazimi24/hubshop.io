"use client";

import Link from "next/link";
import { Eye, AtSign, Users, TrendingUp, ArrowRight, Upload } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { cn } from "@/lib/utils";

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
  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Post Reach" value="1.2M" icon={Eye} trend={{ value: 18, direction: "up" }} />
          <MetricCard label="Brand Mentions" value={342} icon={AtSign} trend={{ value: 24, direction: "up" }} />
          <MetricCard label="Followers" value="48.2K" icon={Users} trend={{ value: 3, direction: "up" }} />
          <MetricCard label="Engagement Rate" value="5.8%" icon={TrendingUp} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Mention spike" description="Brand mentions increased 24% this week. Positive sentiment dominates at 68%." variant="success" />
          <InsightItem title="Best posting time" description="Friday 6:00 PM shows 'Very High' engagement. Schedule your next post then." />
        </InsightPanel>
      }
    >
      <h3 className="text-sm font-semibold text-gray-900 mb-4">Organic Modules</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {QUICK_LINKS.map((mod) => {
          const Icon = mod.icon;
          return (
            <Link
              key={mod.title}
              href={mod.href}
              className="group relative overflow-hidden rounded-xl border border-gray-100 bg-white p-5 hover:shadow-md hover:border-gray-200 transition-all duration-200"
            >
              <div className={cn("absolute inset-0 bg-gradient-to-br opacity-50", mod.gradient)} />
              <div className="relative">
                <div className="flex items-center gap-3 mb-2">
                  <div className={cn("flex h-9 w-9 items-center justify-center rounded-lg", mod.iconBg)}>
                    <Icon className={cn("h-[18px] w-[18px]", mod.iconColor)} />
                  </div>
                  <h3 className="text-sm font-semibold text-gray-900 group-hover:text-gray-700 transition-colors">{mod.title}</h3>
                  <ArrowRight className="ml-auto h-4 w-4 text-gray-300 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200" />
                </div>
                <p className="text-xs text-gray-500 leading-relaxed">{mod.description}</p>
              </div>
            </Link>
          );
        })}
      </div>
    </PageShell>
  );
}
