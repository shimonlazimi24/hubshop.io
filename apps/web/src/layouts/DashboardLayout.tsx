import { motion } from "framer-motion";
import { useCallback, useEffect, useState } from "react";
import {
  Navigate,
  Outlet,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { CommandPalette } from "@/components/dashboard/command-palette";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { Skeleton } from "@/components/ui/skeleton";
import { ToastContainer } from "@/components/ui/toast";
import { useSidebarState } from "@/hooks/useSidebarState";
import { getApiPrefix } from "@/lib/api";
import {
  clearProfile,
  fetchSessionUser,
  type SessionUser,
} from "@/lib/user-profile";

function DashboardSkeleton() {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-obsidian">
      <div className="hidden w-64 flex-col gap-4 border-r border-gray-200 bg-white p-4 dark:border-zinc-800 dark:bg-obsidian-light md:flex">
        <Skeleton className="h-8 w-24" />
        <div className="mt-4 space-y-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </div>
      </div>
      <div className="flex-1 p-8">
        <Skeleton className="mb-6 h-6 w-48" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full rounded-xl" />
          ))}
        </div>
      </div>
    </div>
  );
}

export function DashboardLayout() {
  const nav = useNavigate();
  const { pathname } = useLocation();
  const [user, setUser] = useState<SessionUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const { collapsed, toggle } = useSidebarState();

  useEffect(() => {
    const token = localStorage.getItem("frodo_access_token");
    if (!token) {
      nav("/login", { replace: true });
      return;
    }

    void fetchSessionUser(token).then((u) => {
      if (!u) {
        localStorage.removeItem("frodo_access_token");
        localStorage.removeItem("frodo_refresh_token");
        localStorage.removeItem("frodo_workspace_id");
        localStorage.removeItem("frodo_last_shop_id");
        clearProfile();
        nav("/login", { replace: true });
        setLoading(false);
        return;
      }
      setUser(u);
      setLoading(false);
    });
  }, [nav]);

  const handleLogout = useCallback(async () => {
    const t = localStorage.getItem("frodo_access_token");
    if (t) {
      await fetch(`${getApiPrefix()}/api/auth/logout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${t}`,
        },
      }).catch(() => undefined);
    }
    localStorage.removeItem("frodo_access_token");
    localStorage.removeItem("frodo_refresh_token");
    localStorage.removeItem("frodo_workspace_id");
    localStorage.removeItem("frodo_last_shop_id");
    clearProfile();
    nav("/login", { replace: true });
  }, [nav]);

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

  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-obsidian">
      <div className="fixed inset-x-0 top-0 z-50 h-0.5 gradient-bg-horizontal" />

      <Sidebar
        collapsed={collapsed}
        onToggle={toggle}
        user={user}
        onLogout={() => void handleLogout()}
      />

      <div className="flex flex-1 flex-col overflow-hidden pt-0.5">
        <TopBar
          onOpenCommandPalette={() => setCommandPaletteOpen(true)}
          user={user}
          onLogout={() => void handleLogout()}
        />

        <main className="flex-1 overflow-y-auto">
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: 0.3,
              ease: [0.25, 0.1, 0.25, 1],
            }}
            className="p-4 md:p-6 lg:p-8"
          >
            <div className="mx-auto max-w-6xl">
              <Outlet />
            </div>
          </motion.div>
        </main>
      </div>

      <CommandPalette
        open={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
      />

      <ToastContainer />
    </div>
  );
}
