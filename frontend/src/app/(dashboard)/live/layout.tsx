"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Radio, Activity, Clock, PlayCircle } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { cn } from "@/lib/utils";

const TABS = [
  {
    href: "/live",
    label: "Active Streams",
    icon: Radio,
    exact: ["/live"],
    prefix: [],
  },
  {
    href: "/live/monitor",
    label: "Monitor",
    icon: PlayCircle,
    exact: [],
    prefix: ["/live/monitor"],
  },
  {
    href: "/live/history",
    label: "History",
    icon: Clock,
    exact: [],
    prefix: ["/live/history"],
  },
];

export default function LiveLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // Don't show tabs on session detail pages (they have their own navigation)
  const isSessionPage = /^\/live\/[^/]+$/.test(pathname) && pathname !== "/live/monitor" && pathname !== "/live/history";
  const isSessionAnalytics = /^\/live\/[^/]+\/analytics$/.test(pathname);

  return (
    <div>
      <PageHeader
        title="LIVE"
        description="Monitor TikTok LIVE streams in real-time, track events, and analyze performance."
      />

      {!isSessionPage && !isSessionAnalytics && (
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
      )}

      {children}
    </div>
  );
}
