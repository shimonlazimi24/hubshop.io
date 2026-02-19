"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Megaphone, Layers, Image, BarChart3 } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { cn } from "@/lib/utils";

const TABS = [
  {
    href: "/ads",
    label: "Campaigns",
    icon: Megaphone,
    exact: ["/ads"],
    prefix: ["/ads/campaigns"],
  },
  {
    href: "/ads/ad-groups",
    label: "Ad Groups",
    icon: Layers,
    exact: [],
    prefix: ["/ads/ad-groups"],
  },
  {
    href: "/ads/creatives",
    label: "Ads",
    icon: Image,
    exact: [],
    prefix: ["/ads/creatives"],
  },
  {
    href: "/ads/reports",
    label: "Reports",
    icon: BarChart3,
    exact: [],
    prefix: ["/ads/reports"],
  },
];

export default function AdsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div>
      <PageHeader
        title="Advertising"
        description="Manage your TikTok ad campaigns, ad groups, and reporting."
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
