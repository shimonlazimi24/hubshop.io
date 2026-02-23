"use client";

import { Megaphone, Layers, Image, BarChart3, UsersRound, Crosshair, BookOpen, Zap, Activity, MessageSquare, Search, Wand2, FlaskConical, UserPlus, Fingerprint } from "lucide-react";
import { PlatformTabLayout, type FeatureTab } from "@/components/ui/platform-tab-layout";

const PLATFORM_TABS = [
  { key: "all", label: "All Platforms" },
  { key: "marketing", label: "TikTok Ads" },
  { key: "shop", label: "Shop Promotions" },
];

const FEATURE_TABS: FeatureTab[] = [
  { href: "/ads", label: "Campaigns", icon: Megaphone, exact: ["/ads"], prefix: ["/ads/campaigns"], platforms: ["marketing", "shop"] },
  { href: "/ads/ad-groups", label: "Ad Groups", icon: Layers, exact: [], prefix: ["/ads/ad-groups"], platforms: ["marketing"] },
  { href: "/ads/creatives", label: "Ads", icon: Image, exact: [], prefix: ["/ads/creatives"], platforms: ["marketing"] },
  { href: "/ads/reports", label: "Reports", icon: BarChart3, exact: [], prefix: ["/ads/reports"], platforms: ["marketing"] },
  { href: "/ads/audiences", label: "Audiences", icon: UsersRound, exact: [], prefix: ["/ads/audiences"], platforms: ["marketing"] },
  { href: "/ads/pixels", label: "Pixels", icon: Crosshair, exact: [], prefix: ["/ads/pixels"], platforms: ["marketing"] },
  { href: "/ads/catalogs", label: "Catalogs", icon: BookOpen, exact: [], prefix: ["/ads/catalogs"], platforms: ["marketing"] },
  { href: "/ads/automation", label: "Automation", icon: Zap, exact: [], prefix: ["/ads/automation"], platforms: ["marketing"] },
  { href: "/ads/events", label: "Events", icon: Activity, exact: [], prefix: ["/ads/events"], platforms: ["marketing"] },
  { href: "/ads/comments", label: "Comments", icon: MessageSquare, exact: [], prefix: ["/ads/comments"], platforms: ["marketing"] },
  { href: "/ads/search", label: "Search Ads", icon: Search, exact: [], prefix: ["/ads/search"], platforms: ["marketing"] },
  { href: "/ads/symphony", label: "Symphony AI", icon: Wand2, exact: [], prefix: ["/ads/symphony"], platforms: ["marketing"] },
  { href: "/ads/split-tests", label: "Split Tests", icon: FlaskConical, exact: [], prefix: ["/ads/split-tests"], platforms: ["marketing"] },
  { href: "/ads/leads", label: "Leads", icon: UserPlus, exact: [], prefix: ["/ads/leads"], platforms: ["marketing"] },
  { href: "/ads/identities", label: "Identities", icon: Fingerprint, exact: [], prefix: ["/ads/identities"], platforms: ["marketing"] },
];

export default function AdsLayout({ children }: { children: React.ReactNode }) {
  return (
    <PlatformTabLayout
      title="Advertising"
      description="Manage your TikTok ad campaigns, ad groups, and reporting."
      platformTabs={PLATFORM_TABS}
      featureTabs={FEATURE_TABS}
    >
      {children}
    </PlatformTabLayout>
  );
}
