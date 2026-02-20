"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, FileText, Bell, Settings, ShoppingBag, Megaphone, Play } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { cn } from "@/lib/utils";

const TABS = [
  {
    href: "/analytics",
    label: "Dashboard",
    icon: BarChart3,
    exact: ["/analytics"],
    prefix: [],
  },
  {
    href: "/analytics/commerce",
    label: "Commerce",
    icon: ShoppingBag,
    exact: [],
    prefix: ["/analytics/commerce"],
  },
  {
    href: "/analytics/advertising",
    label: "Advertising",
    icon: Megaphone,
    exact: [],
    prefix: ["/analytics/advertising"],
  },
  {
    href: "/analytics/content",
    label: "Content",
    icon: Play,
    exact: [],
    prefix: ["/analytics/content"],
  },
  {
    href: "/analytics/reports",
    label: "Reports",
    icon: FileText,
    exact: [],
    prefix: ["/analytics/reports"],
  },
  {
    href: "/analytics/notifications",
    label: "Notifications",
    icon: Bell,
    exact: [],
    prefix: ["/analytics/notifications"],
  },
  {
    href: "/analytics/settings",
    label: "Settings",
    icon: Settings,
    exact: [],
    prefix: ["/analytics/settings"],
  },
];

export default function AnalyticsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div>
      <PageHeader
        title="Analytics"
        description="Unified cross-platform analytics across Shop, Ads, Content, and Creators."
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
