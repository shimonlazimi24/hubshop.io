"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Suspense, useEffect } from "react";
import { ShoppingCart, Package, RotateCcw, TrendingUp, Users, Tag, DollarSign, MessageSquare } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { PlatformTabs } from "@/components/ui/platform-tabs";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
import { cn } from "@/lib/utils";

const COMMERCE_PLATFORM_TABS = [
  { key: "all", label: "All Platforms" },
  { key: "shop", label: "TikTok Shop" },
  { key: "affiliate", label: "Affiliates" },
];

const TABS = [
  { href: "/commerce", label: "Orders", icon: ShoppingCart, exact: ["/commerce"], prefix: ["/commerce/orders"], platforms: ["shop", "affiliate"] },
  { href: "/commerce/products", label: "Products", icon: Package, exact: [], prefix: ["/commerce/products"], platforms: ["shop", "affiliate"] },
  { href: "/commerce/returns", label: "Returns", icon: RotateCcw, exact: [], prefix: ["/commerce/returns"], platforms: ["shop"] },
  { href: "/commerce/affiliate", label: "Affiliate", icon: Users, exact: [], prefix: ["/commerce/affiliate"], platforms: ["affiliate"] },
  { href: "/commerce/promotions", label: "Promotions", icon: Tag, exact: [], prefix: ["/commerce/promotions"], platforms: ["shop"] },
  { href: "/commerce/finance", label: "Finance", icon: DollarSign, exact: [], prefix: ["/commerce/finance"], platforms: ["shop", "affiliate"] },
  { href: "/commerce/messages", label: "Messages", icon: MessageSquare, exact: [], prefix: ["/commerce/messages"], platforms: ["shop"] },
  { href: "/commerce/analytics", label: "Analytics", icon: TrendingUp, exact: [], prefix: ["/commerce/analytics"], platforms: ["shop", "affiliate"] },
];

function CommerceLayoutInner({ children }: { children: React.ReactNode }) {
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
        title="Commerce"
        description="Manage your TikTok Shop products, orders, and fulfillment."
      />

      <PlatformTabs
        tabs={COMMERCE_PLATFORM_TABS}
        value={platform}
        onChange={setPlatform}
      />

      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-1">
          {TABS.map((tab) => {
            const isVisible = visibleTabs.includes(tab);
            if (!isVisible) return null;
            const isActive =
              tab.exact.some((m) => pathname === m) ||
              tab.prefix.some((m) => pathname === m || pathname.startsWith(m + "/"));
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

export default function CommerceLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={null}>
      <CommerceLayoutInner>{children}</CommerceLayoutInner>
    </Suspense>
  );
}
