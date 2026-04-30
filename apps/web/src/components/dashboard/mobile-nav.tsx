import { AnimatePresence, motion } from "framer-motion";
import { LogOut, Menu, X } from "lucide-react";
import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { ALL_NAV_ITEMS } from "@/config/navigation";
import type { LegacyUser } from "@/lib/user-profile";
import { cn } from "@/lib/utils";

interface MobileNavProps {
  user: LegacyUser | null;
  onLogout: () => void;
}

export function MobileNav({ user, onLogout }: MobileNavProps) {
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();

  return (
    <div className="md:hidden">
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex h-10 w-10 items-center justify-center rounded-lg text-gray-600 transition-colors hover:bg-gray-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      <AnimatePresence>
        {open && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm dark:bg-black/40"
              onClick={() => setOpen(false)}
            />
            <motion.aside
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-white shadow-xl dark:bg-zinc-950 dark:border-r dark:border-zinc-800"
            >
              <div className="flex items-center justify-between border-b border-gray-100 p-4 dark:border-zinc-800">
                <div className="flex items-center gap-2.5">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-coral to-purple">
                    <span className="text-sm font-bold text-white">H</span>
                  </div>
                  <span className="text-sm font-semibold text-gray-900 dark:text-zinc-100">
                    Hubshop
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 dark:hover:bg-zinc-800"
                  aria-label="Close menu"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              <nav className="flex-1 space-y-0.5 overflow-y-auto p-3">
                {ALL_NAV_ITEMS.map((item) => {
                  const Icon = item.icon;
                  const isActive =
                    item.href === "/"
                      ? pathname === "/"
                      : pathname === item.href ||
                        pathname.startsWith(`${item.href}/`);

                  if (item.disabled) {
                    return (
                      <div
                        key={item.href}
                        className="flex cursor-not-allowed items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-400 opacity-50 dark:text-zinc-600"
                        aria-disabled
                      >
                        <Icon className="h-[18px] w-[18px] text-gray-400 dark:text-zinc-600" />
                        {item.label}
                      </div>
                    );
                  }

                  return (
                    <NavLink
                      key={item.href}
                      to={item.href}
                      end={item.href === "/"}
                      onClick={() => setOpen(false)}
                      className={cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                        isActive
                          ? "bg-coral/5 text-coral"
                          : "text-gray-600 hover:bg-gray-50 dark:text-zinc-400 dark:hover:bg-zinc-900",
                      )}
                    >
                      <Icon
                        className={cn(
                          "h-[18px] w-[18px]",
                          isActive ? "text-coral" : "text-gray-400 dark:text-zinc-500",
                        )}
                      />
                      {item.label}
                    </NavLink>
                  );
                })}
              </nav>

              {user && (
                <div className="border-t border-gray-100 p-4 dark:border-zinc-800">
                  <div className="mb-3 flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-xs font-medium text-gray-600 dark:bg-zinc-800 dark:text-zinc-300">
                      {user.full_name?.charAt(0)?.toUpperCase() || "U"}
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-gray-700 dark:text-zinc-200">
                        {user.full_name}
                      </p>
                      <p className="truncate text-xs text-gray-400 dark:text-zinc-500">
                        {user.email || "—"}
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setOpen(false);
                      onLogout();
                    }}
                    className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-red-500 transition-colors hover:bg-red-50 dark:hover:bg-red-500/10"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign out
                  </button>
                </div>
              )}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
