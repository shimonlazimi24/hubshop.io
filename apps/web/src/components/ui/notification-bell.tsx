import { AnimatePresence, motion } from "framer-motion";
import {
  Bell,
  CheckCheck,
  Film,
  Megaphone,
  Package,
  RotateCcw,
  ShoppingCart,
  Users,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

export interface Notification {
  id: string;
  type:
    | "order"
    | "shipping"
    | "return"
    | "campaign"
    | "content"
    | "creator"
    | "system";
  title: string;
  description: string;
  timestamp: Date;
  read: boolean;
}

const TYPE_ICONS = {
  order: ShoppingCart,
  shipping: Package,
  return: RotateCcw,
  campaign: Megaphone,
  content: Film,
  creator: Users,
  system: Bell,
} as const;

const TYPE_COLORS = {
  order: "text-blue-500 bg-blue-50 dark:bg-blue-500/10",
  shipping: "text-green-500 bg-green-50 dark:bg-green-500/10",
  return: "text-amber-500 bg-amber-50 dark:bg-amber-500/10",
  campaign: "text-purple bg-purple/10",
  content: "text-cyan bg-cyan/10",
  creator: "text-info bg-info/10",
  system: "text-foreground-secondary bg-surface-alt",
} as const;

function timeAgo(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

const dropdownVariants = {
  hidden: {
    opacity: 0,
    y: -8,
    scale: 0.96,
    transition: { duration: 0.12 },
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: "spring" as const,
      stiffness: 350,
      damping: 25,
    },
  },
};

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const panelRef = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleToggle = useCallback(() => {
    setOpen((prev) => !prev);
  }, []);

  const markAllRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }, []);

  const markOneRead = useCallback((id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n)),
    );
  }, []);

  useEffect(() => {
    if (!open) return;

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }

    function handleClickOutside(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    const timer = setTimeout(() => {
      window.addEventListener("mousedown", handleClickOutside);
    }, 0);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("mousedown", handleClickOutside);
      clearTimeout(timer);
    };
  }, [open]);

  return (
    <div className="relative" ref={panelRef}>
      <button
        type="button"
        onClick={handleToggle}
        className={cn(
          "relative flex h-9 w-9 items-center justify-center rounded-lg transition-colors",
          "text-foreground-secondary hover:bg-surface hover:text-foreground",
          open && "bg-surface text-foreground",
        )}
        aria-label="Notifications"
        aria-expanded={open}
      >
        <Bell className="h-[18px] w-[18px]" />

        <AnimatePresence>
          {unreadCount > 0 && (
            <motion.span
              key="badge"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              transition={{ type: "spring", stiffness: 400, damping: 15 }}
              className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-coral px-1 text-[10px] font-bold text-white"
            >
              {unreadCount > 9 ? "9+" : unreadCount}

              <span className="absolute inset-0 rounded-full bg-coral opacity-40 animate-ping" />
            </motion.span>
          )}
        </AnimatePresence>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            variants={dropdownVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
            className={cn(
              "absolute right-0 top-full z-50 mt-2 w-80 overflow-hidden rounded-xl",
              "border border-border bg-background shadow-[var(--shadow-panel)]",
            )}
          >
            <div className="flex items-center justify-between border-b border-border/50 px-4 py-3">
              <h3 className="text-sm font-semibold text-foreground">
                Notifications
              </h3>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <>
                    <span className="rounded-full bg-coral/10 px-2 py-0.5 text-[10px] font-medium text-coral">
                      {unreadCount} new
                    </span>
                    <button
                      type="button"
                      onClick={markAllRead}
                      className="flex items-center gap-1 text-[11px] font-medium text-foreground-secondary transition-colors hover:text-foreground"
                      aria-label="Mark all as read"
                    >
                      <CheckCheck className="h-3 w-3" />
                      Read all
                    </button>
                  </>
                )}
              </div>
            </div>

            <div className="max-h-80 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center px-4 py-10">
                  <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-surface">
                    <Bell className="h-5 w-5 text-foreground-secondary opacity-40" />
                  </div>
                  <p className="text-sm font-medium text-foreground-secondary">
                    No notifications yet
                  </p>
                  <p className="mt-1 text-xs text-foreground-secondary opacity-60">
                    Activity will appear here in real-time
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-border/50">
                  {notifications.map((notif) => {
                    const Icon = TYPE_ICONS[notif.type];
                    const colorClass = TYPE_COLORS[notif.type];
                    return (
                      <motion.button
                        key={notif.id}
                        type="button"
                        onClick={() => markOneRead(notif.id)}
                        initial={{ opacity: 0, x: -8 }}
                        animate={{ opacity: 1, x: 0 }}
                        className={cn(
                          "flex w-full gap-3 px-4 py-3 text-left transition-colors hover:bg-surface",
                          !notif.read && "bg-coral/[0.02]",
                        )}
                      >
                        <div
                          className={cn(
                            "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg",
                            colorClass,
                          )}
                        >
                          <Icon className="h-4 w-4" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-medium text-foreground">
                            {notif.title}
                          </p>
                          <p className="mt-0.5 truncate text-xs text-foreground-secondary">
                            {notif.description}
                          </p>
                          <p className="mt-1 text-[10px] text-foreground-secondary opacity-60">
                            {timeAgo(notif.timestamp)}
                          </p>
                        </div>
                        {!notif.read && (
                          <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-coral"
                          />
                        )}
                      </motion.button>
                    );
                  })}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
