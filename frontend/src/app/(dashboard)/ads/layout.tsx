"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Suspense, useEffect } from "react";
import { Megaphone, Layers, Image, BarChart3, UsersRound, Crosshair, BookOpen, Zap, Activity, MessageSquare, Search, Wand2, FlaskConical, UserPlus, Fingerprint } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { PlatformTabs } from "@/components/ui/platform-tabs";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
import { cn } from "@/lib/utils";

const ADS_PLATFORM_TABS = [
  { key: "all", label: "All Platforms" },
  { key: "marketing", label: "TikTok Ads" },
  { key: "shop", label: "Shop Promotions" },
];

const TABS = [
  {
    href: "/ads",
    label: "Campaigns",
    icon: Megaphone,
    exact: ["/ads"],
    prefix: ["/ads/campaigns"],
    platforms: ["marketing", "shop"],
  },
  {
    href: "/ads/ad-groups",
    label: "Ad Groups",
    icon: Layers,
    exact: [],
    prefix: ["/ads/ad-groups"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/creatives",
    label: "Ads",
    icon: Image,
    exact: [],
    prefix: ["/ads/creatives"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/reports",
    label: "Reports",
    icon: BarChart3,
    exact: [],
    prefix: ["/ads/reports"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/audiences",
    label: "Audiences",
    icon: UsersRound,
    exact: [],
    prefix: ["/ads/audiences"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/pixels",
    label: "Pixels",
    icon: Crosshair,
    exact: [],
    prefix: ["/ads/pixels"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/catalogs",
    label: "Catalogs",
    icon: BookOpen,
    exact: [],
    prefix: ["/ads/catalogs"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/automation",
    label: "Automation",
    icon: Zap,
    exact: [],
    prefix: ["/ads/automation"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/events",
    label: "Events",
    icon: Activity,
    exact: [],
    prefix: ["/ads/events"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/comments",
    label: "Comments",
    icon: MessageSquare,
    exact: [],
    prefix: ["/ads/comments"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/search",
    label: "Search Ads",
    icon: Search,
    exact: [],
    prefix: ["/ads/search"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/symphony",
    label: "Symphony AI",
    icon: Wand2,
    exact: [],
    prefix: ["/ads/symphony"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/split-tests",
    label: "Split Tests",
    icon: FlaskConical,
    exact: [],
    prefix: ["/ads/split-tests"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/leads",
    label: "Leads",
    icon: UserPlus,
    exact: [],
    prefix: ["/ads/leads"],
    platforms: ["marketing"],
  },
  {
    href: "/ads/identities",
    label: "Identities",
    icon: Fingerprint,
    exact: [],
    prefix: ["/ads/identities"],
    platforms: ["marketing"],
  },
];

function AdsLayoutInner({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { platform, setPlatform } = usePlatformFilter();

  const visibleTabs = platform === "all"
    ? TABS
    : TABS.filter((tab) => tab.platforms.includes(platform));

  const isCurrentPathVisible = visibleTabs.some(
    (tab) =>
      tab.exact.some((m) => pathname === m) ||
      tab.prefix.some((m) => pathname === m || pathname.startsWith(m + "/"))
  );

  useEffect(() => {
    if (!isCurrentPathVisible && visibleTabs.length > 0) {
      const params = new URLSearchParams();
      if (platform !== "all") params.set("platform", platform);
      const qs = params.toString();
      const target = qs ? `${visibleTabs[0].href}?${qs}` : visibleTabs[0].href;
      router.push(target);
    }
  }, [isCurrentPathVisible, visibleTabs, platform, router]);

  return (
    <div>
      <PageHeader
        title="Advertising"
        description="Manage your TikTok ad campaigns, ad groups, and reporting."
      />

      <PlatformTabs
        tabs={ADS_PLATFORM_TABS}
        value={platform}
        onChange={setPlatform}
      />

      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-1">
          {visibleTabs.map((tab) => {
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

export default function AdsLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={null}>
      <AdsLayoutInner>{children}</AdsLayoutInner>
    </Suspense>
  );
}
