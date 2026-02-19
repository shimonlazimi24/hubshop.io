"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/commerce", label: "Orders", match: ["/commerce", "/commerce/orders"] },
  { href: "/commerce/products", label: "Products", match: ["/commerce/products"] },
  { href: "/commerce/returns", label: "Returns", match: ["/commerce/returns"] },
  { href: "/commerce/analytics", label: "Analytics", match: ["/commerce/analytics"] },
];

export default function CommerceLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-1">Commerce</h2>
        <p className="text-gray-500 text-sm">
          Manage your TikTok Shop products, orders, and fulfillment.
        </p>
      </div>

      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8">
          {TABS.map((tab) => {
            const isActive = tab.match.some(
              (m) => pathname === m || pathname.startsWith(m + "/")
            );
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                  isActive
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
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
