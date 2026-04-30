import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowRight,
  Building2,
  Megaphone,
  Package,
  RefreshCw,
  Search,
  TrendingUp,
  Zap,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ALL_NAV_ITEMS } from "@/config/navigation";
import { cn } from "@/lib/utils";

interface CommandItem {
  id: string;
  label: string;
  description?: string;
  icon: React.ElementType;
  group: "Pages" | "Commerce" | "Actions";
  action: () => void;
}

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
}

const overlayVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};

const panelVariants = {
  hidden: { opacity: 0, scale: 0.92, y: -24 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: "spring" as const,
      damping: 28,
      stiffness: 380,
      mass: 0.8,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: -12,
    transition: { duration: 0.12, ease: "easeIn" as const },
  },
};

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  const lastShopId = localStorage.getItem("frodo_last_shop_id");

  const go = useCallback(
    (path: string) => {
      navigate(path);
      onClose();
    },
    [navigate, onClose],
  );

  const items: CommandItem[] = useMemo(
    () => [
      ...ALL_NAV_ITEMS.filter((item) => !item.disabled).map((item) => ({
        id: item.href.replace(/\//g, "-").slice(1) || "home",
        label: item.label,
        icon: item.icon,
        group: "Pages" as const,
        action: () => go(item.href),
      })),
      {
        id: "workspace",
        label: "Workspace",
        description: "Switch workspace",
        icon: Building2,
        group: "Pages" as const,
        action: () => go("/workspace"),
      },
      {
        id: "shops-list",
        label: "Shops",
        description: "Commerce > Shops & sync status",
        icon: Package,
        group: "Commerce" as const,
        action: () => go("/shops"),
      },
      {
        id: "connect-shop",
        label: "Connect Shop",
        description: "OAuth & discovery",
        icon: Package,
        group: "Commerce" as const,
        action: () => go("/connect/shop"),
      },
      {
        id: "shop-detail",
        label: lastShopId ? "Last opened shop" : "Open a shop",
        description: lastShopId
          ? "Commerce > Products & orders"
          : "Pick a shop from Shops first",
        icon: TrendingUp,
        group: "Commerce" as const,
        action: () => go(lastShopId ? `/shops/${lastShopId}` : "/shops"),
      },
      {
        id: "sync-hint",
        label: "Refresh commerce data",
        description: "Open shop detail to run sync",
        icon: RefreshCw,
        group: "Actions" as const,
        action: () => go(lastShopId ? `/shops/${lastShopId}` : "/shops"),
      },
      {
        id: "campaign-placeholder",
        label: "Advertising",
        description: "Module navigation (preview)",
        icon: Megaphone,
        group: "Actions" as const,
        action: () => go("/shops"),
      },
      {
        id: "settings-sync",
        label: "Workspace settings",
        description: "Tokens & preferences",
        icon: Zap,
        group: "Actions" as const,
        action: () => go("/settings"),
      },
    ],
    [go, lastShopId],
  );

  const filtered = useMemo(() => {
    if (!query.trim()) return items;
    const q = query.toLowerCase();
    return items.filter(
      (item) =>
        item.label.toLowerCase().includes(q) ||
        item.description?.toLowerCase().includes(q) ||
        item.group.toLowerCase().includes(q),
    );
  }, [items, query]);

  const grouped = useMemo(() => {
    const groups: Record<string, CommandItem[]> = {};
    for (const item of filtered) {
      if (!groups[item.group]) groups[item.group] = [];
      groups[item.group].push(item);
    }
    return groups;
  }, [filtered]);

  useEffect(() => {
    if (open) {
      setQuery("");
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;

    function handleKeyDown(e: KeyboardEvent) {
      if (filtered.length === 0) return;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((i) => Math.min(i + 1, filtered.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((i) => Math.max(i - 1, 0));
      } else if (e.key === "Enter" && filtered[selectedIndex]) {
        e.preventDefault();
        filtered[selectedIndex].action();
      } else if (e.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, filtered, selectedIndex, onClose]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  const flatItems = useMemo(() => {
    const result: Array<{
      item: CommandItem;
      groupLabel: string;
      flatIndex: number;
    }> = [];
    let index = 0;
    for (const [group, groupItems] of Object.entries(grouped)) {
      for (const item of groupItems) {
        result.push({ item, groupLabel: group, flatIndex: index++ });
      }
    }
    return result;
  }, [grouped]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            variants={overlayVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm dark:bg-black/60"
            onClick={onClose}
          />

          <motion.div
            variants={panelVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="fixed left-1/2 top-[20%] z-50 w-full max-w-lg -translate-x-1/2 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-2xl dark:border-zinc-700 dark:bg-zinc-900"
          >
            <div className="flex items-center gap-3 border-b border-gray-100 px-4 dark:border-zinc-800">
              <Search className="h-4 w-4 shrink-0 text-gray-400 dark:text-zinc-500" />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search pages, actions..."
                className="flex-1 border-none bg-transparent py-3.5 text-sm text-gray-900 outline-none placeholder:text-gray-400 dark:text-zinc-100 dark:placeholder:text-zinc-500"
              />
              <kbd className="rounded border border-gray-200 bg-gray-50 px-1.5 py-0.5 text-[10px] font-medium text-gray-400 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-500">
                ESC
              </kbd>
            </div>

            <div className="max-h-72 overflow-y-auto py-2">
              {filtered.length === 0 ? (
                <div className="px-4 py-8 text-center">
                  <p className="text-sm text-gray-400 dark:text-zinc-500">
                    No results for &ldquo;{query}&rdquo;
                  </p>
                </div>
              ) : (
                (() => {
                  let lastGroup = "";
                  return flatItems.map(({ item, groupLabel, flatIndex: idx }) => {
                    const showGroupHeader = groupLabel !== lastGroup;
                    lastGroup = groupLabel;
                    const isSelected = idx === selectedIndex;
                    const Icon = item.icon;
                    return (
                      <div key={item.id}>
                        {showGroupHeader && (
                          <p className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-400 dark:text-zinc-500">
                            {groupLabel}
                          </p>
                        )}
                        <button
                          type="button"
                          onClick={() => item.action()}
                          onMouseEnter={() => setSelectedIndex(idx)}
                          className={cn(
                            "flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors",
                            isSelected
                              ? "bg-gray-50 dark:bg-zinc-800"
                              : "hover:bg-gray-50 dark:hover:bg-zinc-800",
                          )}
                        >
                          <Icon
                            className={cn(
                              "h-4 w-4 shrink-0",
                              isSelected
                                ? "text-coral"
                                : "text-gray-400 dark:text-zinc-500",
                            )}
                          />
                          <div className="min-w-0 flex-1">
                            <p
                              className={cn(
                                "text-sm",
                                isSelected
                                  ? "font-medium text-gray-900 dark:text-zinc-100"
                                  : "text-gray-700 dark:text-zinc-300",
                              )}
                            >
                              {item.label}
                            </p>
                            {item.description && (
                              <p className="truncate text-xs text-gray-400 dark:text-zinc-500">
                                {item.description}
                              </p>
                            )}
                          </div>
                          {isSelected && (
                            <ArrowRight className="h-3.5 w-3.5 text-gray-300 dark:text-zinc-600" />
                          )}
                        </button>
                      </div>
                    );
                  });
                })()
              )}
            </div>

            <div className="flex items-center justify-between border-t border-gray-100 px-4 py-2 dark:border-zinc-800">
              <div className="flex items-center gap-3 text-[10px] text-gray-400 dark:text-zinc-500">
                <span>
                  <kbd className="rounded border border-gray-200 bg-gray-50 px-1 py-0.5 font-medium dark:border-zinc-700 dark:bg-zinc-800">
                    &uarr;&darr;
                  </kbd>{" "}
                  Navigate
                </span>
                <span>
                  <kbd className="rounded border border-gray-200 bg-gray-50 px-1 py-0.5 font-medium dark:border-zinc-700 dark:bg-zinc-800">
                    &crarr;
                  </kbd>{" "}
                  Select
                </span>
                <span>
                  <kbd className="rounded border border-gray-200 bg-gray-50 px-1 py-0.5 font-medium dark:border-zinc-700 dark:bg-zinc-800">
                    Esc
                  </kbd>{" "}
                  Close
                </span>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
