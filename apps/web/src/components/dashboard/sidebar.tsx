import { AnimatePresence, motion } from "framer-motion";
import {
  Building2,
  ChevronDown,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  LogOut,
} from "lucide-react";
import { Fragment, useMemo, useState } from "react";
import { NavLink } from "react-router-dom";
import { Tooltip } from "@/components/ui/tooltip";
import { NAV_ITEMS, SETTINGS_ITEM } from "@/config/navigation";
import type { SessionUser } from "@/lib/user-profile";
import { cn } from "@/lib/utils";

const GROUPS = ["Main", "Modules", "Insights"] as const;

const SHORTCUT_HINTS: Record<string, string> = {
  "/": "\u23181",
  "/connect/shop": "\u23182",
};

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  user: SessionUser | null;
  onLogout: () => void;
}

function getInitials(name: string | undefined): string {
  if (!name) return "U";
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

export function Sidebar({
  collapsed,
  onToggle,
  user,
  onLogout,
}: SidebarProps) {
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(
    {
      Main: true,
      Modules: true,
      Insights: true,
    },
  );

  const toggleGroup = (group: string) => {
    setExpandedGroups((prev) => ({ ...prev, [group]: !prev[group] }));
  };

  const groupedItems = useMemo(
    () =>
      GROUPS.map((group) => ({
        group,
        items: NAV_ITEMS.filter((item) => item.group === group),
      })).filter(({ items }) => items.length > 0),
    [],
  );

  function renderNavItem(item: (typeof NAV_ITEMS)[number]) {
    const Icon = item.icon;
    const shortcut = SHORTCUT_HINTS[item.href];

    const activeClass = ({ isActive }: { isActive: boolean }) =>
      cn(
        "group/item relative flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors duration-150",
        isActive ? "text-zinc-100" : "text-zinc-400 hover:text-zinc-200",
        collapsed && "justify-center px-0",
      );

    const pill = (
      <motion.div
        layoutId="sidebar-active-pill"
        className="absolute inset-0 rounded-lg border border-zinc-700/50 bg-zinc-800/80"
        transition={{
          type: "spring",
          stiffness: 350,
          damping: 30,
        }}
      />
    );

    const inner = (isActive: boolean) => (
      <>
        {isActive && pill}
        {!isActive && (
          <span className="absolute inset-0 rounded-lg bg-zinc-800/0 transition-colors duration-150 group-hover/item:bg-zinc-800/50" />
        )}
        <Icon
          className={cn(
            "relative z-10 h-[18px] w-[18px] shrink-0 transition-colors duration-150",
            isActive ? "text-coral" : "text-zinc-500 group-hover/item:text-zinc-300",
          )}
        />
        {!collapsed && (
          <>
            <span className="relative z-10 truncate">{item.label}</span>
            {shortcut && (
              <span className="relative z-10 ml-auto hidden items-center rounded bg-zinc-800 px-1 py-0.5 font-mono text-[9px] text-zinc-500 xl:inline-flex">
                {shortcut}
              </span>
            )}
            {item.badge !== undefined && (
              <span
                className={cn(
                  "relative z-10 ml-auto rounded-full bg-coral/15 px-1.5 py-0.5 text-[10px] font-medium text-coral",
                  typeof item.badge === "number" &&
                    item.badge > 0 &&
                    "animate-pulse-badge",
                )}
              >
                {item.badge}
              </span>
            )}
          </>
        )}
      </>
    );

    if (item.disabled) {
      const disabledRow = (
        <div
          className={cn(
            "relative flex cursor-not-allowed items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium text-zinc-500 opacity-45",
            collapsed && "justify-center px-0",
          )}
          aria-disabled
        >
          <Icon className="relative z-10 h-[18px] w-[18px] shrink-0" />
          {!collapsed && <span className="truncate">{item.label}</span>}
        </div>
      );
      return collapsed ? (
        <Tooltip content={`${item.label} (soon)`} side="right">
          {disabledRow}
        </Tooltip>
      ) : (
        <Tooltip content="Coming soon" side="right">
          {disabledRow}
        </Tooltip>
      );
    }

    const link = (
      <NavLink to={item.href} end={item.href === "/"} className={activeClass}>
        {({ isActive }) => inner(isActive)}
      </NavLink>
    );

    if (collapsed) {
      return (
        <Tooltip content={item.label} side="right">
          {link}
        </Tooltip>
      );
    }

    return link;
  }

  return (
    <motion.aside
      className={cn(
        "hidden flex-col bg-zinc-950 text-zinc-300 transition-colors md:flex",
        "border-r border-zinc-800/60",
      )}
      animate={{ width: collapsed ? 64 : 256 }}
      transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
    >
      <div
        className={cn(
          "border-b border-zinc-800/60",
          collapsed ? "px-3 py-4" : "p-4",
        )}
      >
        <NavLink to="/" className="group flex items-center gap-2.5">
          <div className="animate-logo-shimmer glow-gold-always relative flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-coral to-purple">
            <span className="relative z-10 select-none text-sm font-bold text-white">
              H
            </span>
          </div>

          <AnimatePresence mode="wait">
            {!collapsed && (
              <motion.div
                className="min-w-0"
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
                transition={{ duration: 0.15 }}
              >
                <h1 className="truncate text-sm font-semibold text-zinc-100">
                  Hubshop
                </h1>
                <p className="truncate text-[10px] text-zinc-500">
                  One platform to rule them all
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </NavLink>

        <AnimatePresence>
          {!collapsed && (
            <motion.button
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.15 }}
              type="button"
              className="mt-3 flex w-full items-center gap-2 overflow-hidden rounded-lg border border-zinc-800 px-2.5 py-1.5 text-xs text-zinc-400 transition-colors hover:border-zinc-700 hover:bg-zinc-900"
              aria-disabled="true"
              title="Workspace switcher coming soon"
            >
              <Building2 className="h-3.5 w-3.5 text-zinc-500" />
              <span className="flex-1 truncate text-left">
                {user?.full_name?.split(" ")[0] ?? "My"}&apos;s Workspace
              </span>
              <ChevronDown className="h-3 w-3 text-zinc-500" />
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      <nav className="scrollbar-none flex-1 overflow-y-auto py-3">
        {groupedItems.map(({ group, items }) => {
          const isExpanded = expandedGroups[group] ?? true;

          return (
            <div key={group} className="mb-1">
              {!collapsed ? (
                <button
                  type="button"
                  onClick={() => toggleGroup(group)}
                  className="flex w-full items-center gap-1 px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-zinc-500 transition-colors hover:text-zinc-300"
                >
                  <motion.span
                    animate={{ rotate: isExpanded ? 90 : 0 }}
                    transition={{ duration: 0.15 }}
                    className="flex items-center"
                  >
                    <ChevronRight className="h-3 w-3" />
                  </motion.span>
                  <span>{group}</span>
                </button>
              ) : (
                <div className="mx-auto my-1.5 h-px w-6 bg-zinc-800" />
              )}

              <AnimatePresence initial={false}>
                {(isExpanded || collapsed) && (
                  <motion.div
                    initial={collapsed ? false : { height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                    className="overflow-hidden"
                  >
                    <div className="space-y-0.5 px-2">
                      {items.map((item) => (
                        <Fragment key={item.href}>{renderNavItem(item)}</Fragment>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </nav>

      <div
        className={cn(
          "border-t border-zinc-800/60",
          collapsed ? "px-2 py-3" : "px-2 py-3",
        )}
      >
        {collapsed ? (
          <Tooltip content="Settings" side="right">
            <NavLink
              to={SETTINGS_ITEM.href}
              className={({ isActive }) =>
                cn(
                  "group/item relative flex items-center justify-center rounded-lg py-2 text-sm transition-colors",
                  isActive ? "text-coral" : "text-zinc-500 hover:text-zinc-300",
                )
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.div
                      layoutId="sidebar-active-pill"
                      className="absolute inset-0 rounded-lg border border-zinc-700/50 bg-zinc-800/80"
                      transition={{
                        type: "spring",
                        stiffness: 350,
                        damping: 30,
                      }}
                    />
                  )}
                  <SETTINGS_ITEM.icon className="relative z-10 h-[18px] w-[18px]" />
                </>
              )}
            </NavLink>
          </Tooltip>
        ) : (
          <NavLink
            to={SETTINGS_ITEM.href}
            className={({ isActive }) =>
              cn(
                "group/item relative flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors",
                isActive ? "text-zinc-100" : "text-zinc-400 hover:text-zinc-200",
              )
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active-pill"
                    className="absolute inset-0 rounded-lg border border-zinc-700/50 bg-zinc-800/80"
                    transition={{
                      type: "spring",
                      stiffness: 350,
                      damping: 30,
                    }}
                  />
                )}
                {!isActive && (
                  <span className="absolute inset-0 rounded-lg bg-zinc-800/0 transition-colors duration-150 group-hover/item:bg-zinc-800/50" />
                )}
                <SETTINGS_ITEM.icon
                  className={cn(
                    "relative z-10 h-[18px] w-[18px]",
                    isActive ? "text-coral" : "text-zinc-500",
                  )}
                />
                <span className="relative z-10">Settings</span>
              </>
            )}
          </NavLink>
        )}

        <AnimatePresence>
          {!collapsed && user && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.15 }}
              className="mt-2 flex items-center gap-2 overflow-hidden rounded-lg px-2.5 py-2"
            >
              <div className="glow-coral relative flex h-7 w-7 shrink-0 select-none items-center justify-center rounded-full bg-gradient-to-br from-coral via-purple to-gold text-[10px] font-bold text-white">
                {getInitials(user.full_name)}
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-medium text-zinc-200">
                  {user.full_name}
                </p>
                <p className="truncate text-[10px] text-zinc-500">
                  {user.email || "—"}
                </p>
              </div>
              <button
                type="button"
                onClick={onLogout}
                className="text-[10px] text-zinc-500 transition-colors hover:text-red-400"
              >
                Sign out
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {collapsed && (
          <Tooltip content="Sign out" side="right">
            <button
              type="button"
              onClick={onLogout}
              className="mt-1 flex w-full items-center justify-center rounded-lg py-2 text-zinc-500 transition-colors hover:bg-red-950/40 hover:text-red-400"
            >
              <LogOut className="h-[18px] w-[18px]" />
            </button>
          </Tooltip>
        )}

        <button
          type="button"
          onClick={onToggle}
          className="mt-1 flex w-full items-center justify-center rounded-lg py-1.5 text-zinc-500 transition-colors hover:bg-zinc-800/50 hover:text-zinc-300"
        >
          {collapsed ? (
            <ChevronsRight className="h-4 w-4" />
          ) : (
            <div className="flex w-full items-center gap-2 px-2.5">
              <ChevronsLeft className="h-4 w-4" />
              <span className="text-xs">Collapse</span>
            </div>
          )}
        </button>
      </div>
    </motion.aside>
  );
}
