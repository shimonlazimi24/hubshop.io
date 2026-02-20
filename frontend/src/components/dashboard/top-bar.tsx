"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Search, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { NotificationBell } from "./notification-bell";
import { MobileNav } from "./mobile-nav";
import type { UserResponse } from "@/lib/api";

function useBreadcrumbs() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  return segments.map((segment, index) => {
    const href = "/" + segments.slice(0, index + 1).join("/");
    const isId = /^[0-9a-f-]{8,}$/i.test(segment);
    const label = isId
      ? `#${segment.slice(0, 8)}`
      : segment
          .replace(/[-_]/g, " ")
          .replace(/\b\w/g, (c) => c.toUpperCase());

    return { label, href, isLast: index === segments.length - 1 };
  });
}

interface TopBarProps {
  onOpenCommandPalette: () => void;
  user: UserResponse | null;
  onLogout: () => void;
}

export function TopBar({ onOpenCommandPalette, user, onLogout }: TopBarProps) {
  const breadcrumbs = useBreadcrumbs();
  const [isMac, setIsMac] = useState(false);

  useEffect(() => {
    setIsMac(/Mac/i.test(navigator.userAgent));
  }, []);

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-gray-100 bg-white/80 backdrop-blur-md px-4 md:px-6">
      {/* Left: Mobile nav + Breadcrumbs */}
      <div className="flex items-center gap-3">
        <MobileNav user={user} onLogout={onLogout} />

        <nav className="hidden md:flex items-center gap-1 text-sm">
          {breadcrumbs.map((crumb, i) => (
            <div key={crumb.href} className="flex items-center gap-1">
              {i > 0 && <ChevronRight className="h-3.5 w-3.5 text-gray-300" />}
              {crumb.isLast ? (
                <span className="font-medium text-gray-900">{crumb.label}</span>
              ) : (
                <Link
                  href={crumb.href}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {crumb.label}
                </Link>
              )}
            </div>
          ))}
        </nav>
      </div>

      {/* Right: Search + Notifications */}
      <div className="flex items-center gap-2">
        <button
          onClick={onOpenCommandPalette}
          className={cn(
            "flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-400 hover:border-gray-300 hover:text-gray-500 transition-colors",
            "hidden sm:flex"
          )}
        >
          <Search className="h-3.5 w-3.5" />
          <span>Search...</span>
          <kbd className="ml-2 rounded border border-gray-200 bg-gray-50 px-1.5 py-0.5 text-[10px] font-medium text-gray-400">
            {isMac ? "\u2318" : "Ctrl+"}K
          </kbd>
        </button>

        {/* Mobile search button */}
        <button
          onClick={onOpenCommandPalette}
          className="flex sm:hidden h-9 w-9 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 transition-colors"
          aria-label="Search"
        >
          <Search className="h-4 w-4" />
        </button>

        <NotificationBell />
      </div>
    </header>
  );
}
