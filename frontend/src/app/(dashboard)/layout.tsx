"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getMe, type UserResponse } from "@/lib/api";
import { clearTokens, getAccessToken, isAuthenticated } from "@/lib/auth";

const NAV_ITEMS = [
  { href: "/overview", label: "Overview", icon: "grid" },
  { href: "/connect", label: "Connect", icon: "link" },
  { href: "/commerce", label: "Commerce", icon: "shopping-bag" },
  { href: "/ads", label: "Advertising", icon: "megaphone" },
  { href: "/content", label: "Content", icon: "video" },
  { href: "/creators", label: "Creators", icon: "users" },
  { href: "/analytics", label: "Analytics", icon: "bar-chart" },
  { href: "/settings", label: "Settings", icon: "settings" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<UserResponse | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    const token = getAccessToken();
    if (token) {
      getMe(token).then(setUser).catch(() => {
        clearTokens();
        router.push("/login");
      });
    }
  }, [router]);

  function handleLogout() {
    clearTokens();
    router.push("/login");
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">Frodo</h1>
          <p className="text-xs text-gray-500 mt-1">Unified TikTok Platform</p>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-blue-50 text-blue-700"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-gray-200">
          {user && (
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
              <p className="text-xs text-gray-500">{user.email}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
