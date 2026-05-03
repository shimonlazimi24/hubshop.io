import { AnimatePresence, motion } from "framer-motion";
import {
  ChevronDown,
  ChevronRight,
  LogOut,
  Moon,
  Search,
  Settings,
  Sun,
  User,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { NotificationBell } from "@/components/ui/notification-bell";
import type { SessionUser } from "@/lib/user-profile";
import { cn } from "@/lib/utils";
import { MobileNav } from "./mobile-nav";

function useBreadcrumbs() {
  const { pathname } = useLocation();
  const segments = pathname.split("/").filter(Boolean);

  return segments.map((segment, index) => {
    const href = `/${segments.slice(0, index + 1).join("/")}`;
    const isId = /^[0-9a-f-]{8,}$/i.test(segment);
    const label = isId
      ? `#${segment.slice(0, 8)}`
      : segment.replace(/[-_]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

    return { label, href, isLast: index === segments.length - 1 };
  });
}

function useThemeToggle() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    setIsDark(root.classList.contains("dark"));
  }, []);

  const toggle = useCallback(() => {
    const root = document.documentElement;
    const next = !root.classList.contains("dark");
    root.classList.toggle("dark", next);
    setIsDark(next);
    try {
      localStorage.setItem("frodo_theme", next ? "dark" : "light");
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("frodo_theme");
      if (stored === "dark") {
        document.documentElement.classList.add("dark");
        setIsDark(true);
      } else if (stored === "light") {
        document.documentElement.classList.remove("dark");
        setIsDark(false);
      } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        document.documentElement.classList.add("dark");
        setIsDark(true);
      }
    } catch {
      // ignore
    }
  }, []);

  return { isDark, toggle };
}

function UserAvatarDropdown({
  user,
  onLogout,
}: {
  user: SessionUser | null;
  onLogout: () => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!menuOpen) return;
    function handleClickOutside(e: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setMenuOpen(false);
      }
    }
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setMenuOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [menuOpen]);

  if (!user) return null;

  const initials =
    user.full_name
      ?.split(" ")
      .map((n) => n.charAt(0))
      .join("")
      .toUpperCase()
      .slice(0, 2) || "U";

  return (
    <div ref={dropdownRef} className="relative">
      <button
        type="button"
        onClick={() => setMenuOpen((p) => !p)}
        className="flex items-center gap-2 rounded-lg px-1.5 py-1 transition-colors hover:bg-gray-100 dark:hover:bg-zinc-800"
        aria-label="User menu"
      >
        <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-coral to-purple text-[11px] font-semibold text-white">
          {initials}
        </div>
        <ChevronDown
          className={cn(
            "h-3 w-3 text-gray-400 transition-transform duration-150 dark:text-zinc-500",
            menuOpen && "rotate-180",
          )}
        />
      </button>

      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -4, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -4, scale: 0.95 }}
            transition={{ duration: 0.12 }}
            className="absolute right-0 top-full z-50 mt-2 w-56 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-lg dark:border-zinc-700 dark:bg-zinc-900"
          >
            <div className="border-b border-gray-100 px-4 py-3 dark:border-zinc-800">
              <p className="truncate text-sm font-medium text-gray-900 dark:text-zinc-100">
                {user.full_name}
              </p>
              <p className="truncate text-xs text-gray-400 dark:text-zinc-500">
                {user.email || "—"}
              </p>
            </div>

            <div className="py-1">
              <Link
                to="/settings"
                onClick={() => setMenuOpen(false)}
                className="flex items-center gap-2.5 px-4 py-2 text-sm text-gray-600 transition-colors hover:bg-gray-50 dark:text-zinc-400 dark:hover:bg-zinc-800"
              >
                <Settings className="h-3.5 w-3.5" />
                Settings
              </Link>
              <Link
                to="/workspace"
                onClick={() => setMenuOpen(false)}
                className="flex items-center gap-2.5 px-4 py-2 text-sm text-gray-600 transition-colors hover:bg-gray-50 dark:text-zinc-400 dark:hover:bg-zinc-800"
              >
                <User className="h-3.5 w-3.5" />
                Workspace
              </Link>
            </div>

            <div className="border-t border-gray-100 py-1 dark:border-zinc-800">
              <button
                type="button"
                onClick={() => {
                  setMenuOpen(false);
                  onLogout();
                }}
                className="flex w-full items-center gap-2.5 px-4 py-2 text-sm text-red-500 transition-colors hover:bg-red-50 dark:hover:bg-red-500/10"
              >
                <LogOut className="h-3.5 w-3.5" />
                Sign out
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface TopBarProps {
  onOpenCommandPalette: () => void;
  user: SessionUser | null;
  onLogout: () => void;
}

export function TopBar({ onOpenCommandPalette, user, onLogout }: TopBarProps) {
  const breadcrumbs = useBreadcrumbs();
  const [isMac, setIsMac] = useState(false);
  const { isDark, toggle: toggleTheme } = useThemeToggle();

  useEffect(() => {
    setIsMac(/Mac/i.test(navigator.userAgent));
  }, []);

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-gray-100 bg-white/80 px-4 backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-950/80 md:px-6">
      <div className="flex items-center gap-3">
        <MobileNav user={user} onLogout={onLogout} />

        <nav className="hidden items-center gap-1 text-sm md:flex">
          {breadcrumbs.length === 0 ? (
            <span className="font-medium text-gray-900 dark:text-zinc-100">
              Overview
            </span>
          ) : (
            breadcrumbs.map((crumb, i) => (
              <div key={crumb.href} className="flex items-center gap-1">
                {i > 0 && (
                  <ChevronRight className="h-3.5 w-3.5 text-gray-300 dark:text-zinc-600" />
                )}
                {crumb.isLast ? (
                  <span className="font-medium text-gray-900 dark:text-zinc-100">
                    {crumb.label}
                  </span>
                ) : (
                  <Link
                    to={crumb.href}
                    className="text-gray-400 transition-colors hover:text-gray-600 dark:text-zinc-500 dark:hover:text-zinc-300"
                  >
                    {crumb.label}
                  </Link>
                )}
              </div>
            ))
          )}
        </nav>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onOpenCommandPalette}
          className={cn(
            "hidden items-center gap-2 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-400 transition-colors hover:border-gray-300 hover:text-gray-500 dark:border-zinc-700 dark:text-zinc-500 dark:hover:border-zinc-600 dark:hover:text-zinc-400 sm:flex",
          )}
        >
          <Search className="h-3.5 w-3.5" />
          <span>Search...</span>
          <kbd className="ml-2 rounded border border-gray-200 bg-gray-50 px-1.5 py-0.5 text-[10px] font-medium text-gray-400 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-500">
            {isMac ? "\u2318" : "Ctrl+"}K
          </kbd>
        </button>

        <button
          type="button"
          onClick={onOpenCommandPalette}
          className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-400 transition-colors hover:bg-gray-100 dark:text-zinc-500 dark:hover:bg-zinc-800 sm:hidden"
          aria-label="Search"
        >
          <Search className="h-4 w-4" />
        </button>

        <button
          type="button"
          onClick={toggleTheme}
          className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 dark:text-zinc-500 dark:hover:bg-zinc-800 dark:hover:text-zinc-300"
          aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
        >
          {isDark ? (
            <Sun className="h-[18px] w-[18px]" />
          ) : (
            <Moon className="h-[18px] w-[18px]" />
          )}
        </button>

        <NotificationBell />

        <UserAvatarDropdown user={user} onLogout={onLogout} />
      </div>
    </header>
  );
}
