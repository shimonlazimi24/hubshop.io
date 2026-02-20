"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";

import { getMe, type UserResponse } from "@/lib/api";
import { clearTokens, getAccessToken, isAuthenticated } from "@/lib/auth";
import { useSidebarState } from "@/hooks/useSidebarState";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { CommandPalette } from "@/components/dashboard/command-palette";
import { Skeleton } from "@/components/ui/skeleton";

function DashboardSkeleton() {
  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar skeleton */}
      <div className="hidden md:flex w-64 flex-col border-r border-gray-200 bg-white p-4 gap-4">
        <Skeleton className="h-8 w-24" />
        <div className="space-y-2 mt-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </div>
      </div>
      {/* Main skeleton */}
      <div className="flex-1 p-8">
        <Skeleton className="h-6 w-48 mb-6" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full rounded-xl" />
          ))}
        </div>
      </div>
    </div>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const { collapsed, toggle } = useSidebarState();

  useEffect(() => {
    // DEV MODE: skip auth when backend is not running
    const isDev = process.env.NODE_ENV === "development";

    if (!isAuthenticated()) {
      if (isDev) {
        setUser({ id: "dev", email: "admin@frodo.dev", full_name: "Amit Kolton", is_active: true });
        setLoading(false);
        return;
      }
      router.push("/login");
      return;
    }
    const token = getAccessToken();
    if (token) {
      getMe(token)
        .then(setUser)
        .catch(() => {
          if (isDev) {
            setUser({ id: "dev", email: "admin@frodo.dev", full_name: "Amit Kolton", is_active: true });
            setLoading(false);
            return;
          }
          clearTokens();
          router.push("/login");
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [router]);

  const handleLogout = useCallback(() => {
    clearTokens();
    router.push("/login");
  }, [router]);

  // Global Cmd+K shortcut
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen((prev) => !prev);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  if (loading) return <DashboardSkeleton />;

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Gradient accent line */}
      <div className="fixed inset-x-0 top-0 z-50 h-0.5 gradient-bg-horizontal" />

      {/* Sidebar */}
      <Sidebar
        collapsed={collapsed}
        onToggle={toggle}
        user={user}
        onLogout={handleLogout}
      />

      {/* Main area */}
      <div className="flex flex-1 flex-col overflow-hidden pt-0.5">
        <TopBar
          onOpenCommandPalette={() => setCommandPaletteOpen(true)}
          user={user}
          onLogout={handleLogout}
        />

        {/* Page content with subtle fade transition */}
        <main className="flex-1 overflow-y-auto">
          <motion.div
            key={pathname}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="p-4 md:p-6 lg:p-8"
          >
            {children}
          </motion.div>
        </main>
      </div>

      {/* Command Palette overlay */}
      <CommandPalette
        open={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
      />
    </div>
  );
}
