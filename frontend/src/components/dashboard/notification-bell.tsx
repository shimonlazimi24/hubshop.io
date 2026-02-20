"use client";

import { useCallback, useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Bell, Package, RotateCcw, ShoppingCart, X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface Notification {
  id: string;
  type: "order_status_change" | "package_update" | "return_status_change" | "cancellation_status_change";
  title: string;
  description: string;
  timestamp: Date;
  read: boolean;
}

const TYPE_ICONS = {
  order_status_change: ShoppingCart,
  package_update: Package,
  return_status_change: RotateCcw,
  cancellation_status_change: X,
} as const;

const TYPE_COLORS = {
  order_status_change: "text-blue-500 bg-blue-50",
  package_update: "text-green-500 bg-green-50",
  return_status_change: "text-amber-500 bg-amber-50",
  cancellation_status_change: "text-red-500 bg-red-50",
} as const;

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [notifications] = useState<Notification[]>([]);
  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleToggle = useCallback(() => {
    setOpen((prev) => !prev);
  }, []);

  // Close on Escape
  useEffect(() => {
    if (!open) return;
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open]);

  return (
    <div className="relative">
      <button
        onClick={handleToggle}
        className="relative flex h-9 w-9 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
        aria-label="Notifications"
      >
        <Bell className="h-[18px] w-[18px]" />
        {unreadCount > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-coral px-1 text-[10px] font-bold text-white">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      <AnimatePresence>
        {open && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 cursor-default"
              onClick={() => setOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, y: -8, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -8, scale: 0.96 }}
              transition={{ duration: 0.15 }}
              className="absolute right-0 top-full z-50 mt-2 w-80 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-lg"
            >
              <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
                <h3 className="text-sm font-semibold text-gray-900">Notifications</h3>
                {unreadCount > 0 && (
                  <span className="rounded-full bg-coral/10 px-2 py-0.5 text-[10px] font-medium text-coral">
                    {unreadCount} new
                  </span>
                )}
              </div>

              <div className="max-h-80 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-10 px-4">
                    <Bell className="h-8 w-8 text-gray-200 mb-2" />
                    <p className="text-sm text-gray-400">No notifications yet</p>
                    <p className="text-xs text-gray-300 mt-1">
                      Activity will appear here in real-time
                    </p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-50">
                    {notifications.map((notif) => {
                      const Icon = TYPE_ICONS[notif.type];
                      const colorClass = TYPE_COLORS[notif.type];
                      return (
                        <div
                          key={notif.id}
                          className={cn(
                            "flex gap-3 px-4 py-3 hover:bg-gray-50 transition-colors cursor-pointer",
                            !notif.read && "bg-coral/[0.02]"
                          )}
                        >
                          <div className={cn("flex h-8 w-8 shrink-0 items-center justify-center rounded-lg", colorClass)}>
                            <Icon className="h-4 w-4" />
                          </div>
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium text-gray-700 truncate">{notif.title}</p>
                            <p className="text-xs text-gray-400 mt-0.5 truncate">{notif.description}</p>
                          </div>
                          {!notif.read && (
                            <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-coral" />
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
