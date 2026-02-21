"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Library, BarChart3, Wand2 } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { cn } from "@/lib/utils";

const TABS = [
  {
    href: "/creatives",
    label: "Library",
    icon: Library,
    exact: ["/creatives"],
    prefix: [],
  },
  {
    href: "/creatives/performance",
    label: "Performance",
    icon: BarChart3,
    exact: [],
    prefix: ["/creatives/performance"],
  },
  {
    href: "/creatives/generate",
    label: "Generate",
    icon: Wand2,
    exact: [],
    prefix: ["/creatives/generate"],
  },
];

export default function CreativesLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div>
      <PageHeader
        title="Creative Hub"
        description="Your unified creative library and performance command center."
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
