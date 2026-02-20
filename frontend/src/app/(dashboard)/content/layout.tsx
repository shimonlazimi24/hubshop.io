"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Film, Upload, BarChart3, Calendar } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { cn } from "@/lib/utils";

const TABS = [
  { href: "/content", label: "Videos", icon: Film, exact: ["/content"], prefix: ["/content/videos"] },
  { href: "/content/publish", label: "Publish", icon: Upload, exact: [], prefix: ["/content/publish"] },
  { href: "/content/calendar", label: "Calendar", icon: Calendar, exact: [], prefix: ["/content/calendar"] },
  { href: "/content/analytics", label: "Analytics", icon: BarChart3, exact: [], prefix: ["/content/analytics"] },
];

export default function ContentLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div>
      <PageHeader
        title="Content"
        description="View your TikTok videos, publish content, and track performance."
      />

      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-1">
          {TABS.map((tab) => {
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
