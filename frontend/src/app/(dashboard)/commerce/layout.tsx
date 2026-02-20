"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShoppingCart, Package, RotateCcw, TrendingUp, Users, Tag, DollarSign, MessageSquare } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { cn } from "@/lib/utils";

const TABS = [
  { href: "/commerce", label: "Orders", icon: ShoppingCart, exact: ["/commerce"], prefix: ["/commerce/orders"] },
  { href: "/commerce/products", label: "Products", icon: Package, exact: [], prefix: ["/commerce/products"] },
  { href: "/commerce/returns", label: "Returns", icon: RotateCcw, exact: [], prefix: ["/commerce/returns"] },
  { href: "/commerce/affiliate", label: "Affiliate", icon: Users, exact: [], prefix: ["/commerce/affiliate"] },
  { href: "/commerce/promotions", label: "Promotions", icon: Tag, exact: [], prefix: ["/commerce/promotions"] },
  { href: "/commerce/finance", label: "Finance", icon: DollarSign, exact: [], prefix: ["/commerce/finance"] },
  { href: "/commerce/messages", label: "Messages", icon: MessageSquare, exact: [], prefix: ["/commerce/messages"] },
  { href: "/commerce/analytics", label: "Analytics", icon: TrendingUp, exact: [], prefix: ["/commerce/analytics"] },
];

export default function CommerceLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div>
      <PageHeader
        title="Commerce"
        description="Manage your TikTok Shop products, orders, and fulfillment."
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
