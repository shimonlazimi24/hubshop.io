"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Megaphone, Layers, Image, BarChart3, UsersRound, Crosshair, BookOpen, Zap, Activity, MessageSquare, Search, Wand2, FlaskConical, UserPlus, Fingerprint } from "lucide-react";
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
  {
    href: "/ads/audiences",
    label: "Audiences",
    icon: UsersRound,
    exact: [],
    prefix: ["/ads/audiences"],
  },
  {
    href: "/ads/pixels",
    label: "Pixels",
    icon: Crosshair,
    exact: [],
    prefix: ["/ads/pixels"],
  },
  {
    href: "/ads/catalogs",
    label: "Catalogs",
    icon: BookOpen,
    exact: [],
    prefix: ["/ads/catalogs"],
  },
  {
    href: "/ads/automation",
    label: "Automation",
    icon: Zap,
    exact: [],
    prefix: ["/ads/automation"],
  },
  {
    href: "/ads/events",
    label: "Events",
    icon: Activity,
    exact: [],
    prefix: ["/ads/events"],
  },
  {
    href: "/ads/comments",
    label: "Comments",
    icon: MessageSquare,
    exact: [],
    prefix: ["/ads/comments"],
  },
  {
    href: "/ads/search",
    label: "Search Ads",
    icon: Search,
    exact: [],
    prefix: ["/ads/search"],
  },
  {
    href: "/ads/symphony",
    label: "Symphony AI",
    icon: Wand2,
    exact: [],
    prefix: ["/ads/symphony"],
  },
  {
    href: "/ads/split-tests",
    label: "Split Tests",
    icon: FlaskConical,
    exact: [],
    prefix: ["/ads/split-tests"],
  },
  {
    href: "/ads/leads",
    label: "Leads",
    icon: UserPlus,
    exact: [],
    prefix: ["/ads/leads"],
  },
  {
    href: "/ads/identities",
    label: "Identities",
    icon: Fingerprint,
    exact: [],
    prefix: ["/ads/identities"],
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
