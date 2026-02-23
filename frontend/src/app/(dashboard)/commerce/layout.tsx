"use client";

import { ShoppingCart, Package, RotateCcw, TrendingUp, Users, Tag, DollarSign, MessageSquare } from "lucide-react";
import { PlatformTabLayout, type FeatureTab } from "@/components/ui/platform-tab-layout";

const PLATFORM_TABS = [
  { key: "all", label: "All Platforms" },
  { key: "shop", label: "TikTok Shop" },
  { key: "affiliate", label: "Affiliates" },
];

const FEATURE_TABS: FeatureTab[] = [
  { href: "/commerce", label: "Orders", icon: ShoppingCart, exact: ["/commerce"], prefix: ["/commerce/orders"], platforms: ["shop", "affiliate"] },
  { href: "/commerce/products", label: "Products", icon: Package, exact: [], prefix: ["/commerce/products"], platforms: ["shop", "affiliate"] },
  { href: "/commerce/returns", label: "Returns", icon: RotateCcw, exact: [], prefix: ["/commerce/returns"], platforms: ["shop"] },
  { href: "/commerce/affiliate", label: "Affiliate", icon: Users, exact: [], prefix: ["/commerce/affiliate"], platforms: ["affiliate"] },
  { href: "/commerce/promotions", label: "Promotions", icon: Tag, exact: [], prefix: ["/commerce/promotions"], platforms: ["shop"] },
  { href: "/commerce/finance", label: "Finance", icon: DollarSign, exact: [], prefix: ["/commerce/finance"], platforms: ["shop", "affiliate"] },
  { href: "/commerce/messages", label: "Messages", icon: MessageSquare, exact: [], prefix: ["/commerce/messages"], platforms: ["shop"] },
  { href: "/commerce/analytics", label: "Analytics", icon: TrendingUp, exact: [], prefix: ["/commerce/analytics"], platforms: ["shop", "affiliate"] },
];

export default function CommerceLayout({ children }: { children: React.ReactNode }) {
  return (
    <PlatformTabLayout
      title="Commerce"
      description="Manage your TikTok Shop products, orders, and fulfillment."
      platformTabs={PLATFORM_TABS}
      featureTabs={FEATURE_TABS}
    >
      {children}
    </PlatformTabLayout>
  );
}
