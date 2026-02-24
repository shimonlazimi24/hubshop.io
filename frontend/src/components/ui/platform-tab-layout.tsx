"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Suspense, useEffect } from "react";
import type { LucideIcon } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { PlatformTabs, type PlatformTab } from "@/components/ui/platform-tabs";
import { usePlatformFilter } from "@/hooks/usePlatformFilter";
import { cn } from "@/lib/utils";

export interface FeatureTab {
  href: string;
  label: string;
  icon: LucideIcon;
  exact: string[];
  prefix: string[];
  platforms: string[];
}

interface PlatformTabLayoutProps {
  title: string;
  description: string;
  platformTabs: PlatformTab[];
  featureTabs: FeatureTab[];
  children: React.ReactNode;
}

function PlatformTabLayoutInner({
  title,
  description,
  platformTabs,
  featureTabs,
  children,
}: PlatformTabLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { platform, setPlatform } = usePlatformFilter();

  const visibleTabs = platform === "all"
    ? featureTabs
    : featureTabs.filter((tab) => tab.platforms.includes(platform));

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
      <PageHeader title={title} description={description} />

      <PlatformTabs
        tabs={platformTabs}
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
                href={platform !== "all" ? `${tab.href}?platform=${platform}` : tab.href}
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

export function PlatformTabLayout(props: PlatformTabLayoutProps) {
  return (
    <Suspense fallback={null}>
      <PlatformTabLayoutInner {...props} />
    </Suspense>
  );
}
