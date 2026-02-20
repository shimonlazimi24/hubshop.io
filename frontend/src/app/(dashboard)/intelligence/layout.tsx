"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Lightbulb, TrendingUp, Users, Search, Eye } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { cn } from "@/lib/utils";

const TABS = [
  {
    href: "/intelligence",
    label: "Overview",
    icon: Lightbulb,
    exact: ["/intelligence"],
    prefix: [],
  },
  {
    href: "/intelligence/trends",
    label: "Trends",
    icon: TrendingUp,
    exact: [],
    prefix: ["/intelligence/trends"],
  },
  {
    href: "/intelligence/competitors",
    label: "Competitors",
    icon: Eye,
    exact: [],
    prefix: ["/intelligence/competitors"],
  },
  {
    href: "/intelligence/creators",
    label: "Creator Scout",
    icon: Users,
    exact: [],
    prefix: ["/intelligence/creators"],
  },
  {
    href: "/intelligence/research",
    label: "Research",
    icon: Search,
    exact: [],
    prefix: ["/intelligence/research"],
  },
];

export default function IntelligenceLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div>
      <PageHeader
        title="Intelligence"
        description="Market research, trend tracking, competitor analysis, and creator scouting."
      />

      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-1">
          {TABS.map((tab) => {
            const isActive =
              tab.exact.some((m) => pathname === m) ||
              tab.prefix.some(
                (m) => pathname === m || pathname.startsWith(m + "/")
              );
            const Icon = tab.icon;
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cn(
                  "flex items-center gap-1.5 px-3 pb-2.5 text-sm font-medium border-b-2 transition-colors",
                  isActive
                    ? "border-coral text-coral"
                    : "border-transparent text-gray-400 hover:text-gray-600"
                )}
              >
                <Icon className="h-3.5 w-3.5" />
                {tab.label}
              </Link>
            );
          })}
        </nav>
      </div>

      {children}
    </div>
  );
}
