"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ChevronsLeft,
  ChevronsRight,
  Building2,
  ChevronDown,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Tooltip } from "@/components/ui/tooltip";
import { NAV_ITEMS, SETTINGS_ITEM } from "@/config/navigation";
import type { UserResponse } from "@/lib/api";

// Group nav items by their group field
const GROUPS = ["Main", "Modules", "Insights"] as const;

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  user: UserResponse | null;
  onLogout: () => void;
}

export function Sidebar({ collapsed, onToggle, user, onLogout }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "hidden md:flex flex-col border-r border-gray-200 bg-white transition-all duration-200 ease-in-out",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo + Workspace */}
      <div className={cn("border-b border-gray-100", collapsed ? "px-3 py-4" : "p-4")}>
        <Link href="/overview" className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-coral to-purple">
            <span className="text-sm font-bold text-white">F</span>
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <h1 className="text-sm font-semibold text-gray-900 truncate">Frodo</h1>
              <p className="text-[10px] text-gray-400 truncate">One platform to rule them all</p>
            </div>
          )}
        </Link>

        {/* Workspace switcher */}
        {!collapsed && (
          <button
            className="mt-3 flex w-full items-center gap-2 rounded-lg border border-gray-200 px-2.5 py-1.5 text-xs text-gray-600 hover:bg-gray-50 transition-colors"
            aria-disabled="true"
            title="Workspace switcher coming soon"
          >
            <Building2 className="h-3.5 w-3.5 text-gray-400" />
            <span className="flex-1 text-left truncate">
              {user?.full_name?.split(" ")[0] ?? "My"}&apos;s Workspace
            </span>
            <ChevronDown className="h-3 w-3 text-gray-400" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-3">
        {GROUPS.map((group) => {
          const groupItems = NAV_ITEMS.filter((item) => item.group === group);
          if (groupItems.length === 0) return null;
          return (
            <div key={group} className="mb-1">
              {!collapsed && (
                <p className="px-4 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
                  {group}
                </p>
              )}
              {collapsed && <div className="mx-auto my-1 h-px w-6 bg-gray-100" />}
              <div className="space-y-0.5 px-2">
                {groupItems.map((item) => {
                  const isActive =
                    pathname === item.href || pathname.startsWith(item.href + "/");
                  const Icon = item.icon;

                  const link = (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        "group flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium transition-all duration-150",
                        isActive
                          ? "bg-coral/5 text-coral border-l-2 border-coral -ml-px"
                          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900",
                        collapsed && "justify-center px-0"
                      )}
                    >
                      <Icon
                        className={cn(
                          "h-[18px] w-[18px] shrink-0",
                          isActive ? "text-coral" : "text-gray-400 group-hover:text-gray-600"
                        )}
                      />
                      {!collapsed && (
                        <>
                          <span className="truncate">{item.label}</span>
                          {item.badge !== undefined && (
                            <span className="ml-auto rounded-full bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-500">
                              {item.badge}
                            </span>
                          )}
                        </>
                      )}
                    </Link>
                  );

                  if (collapsed) {
                    return (
                      <Tooltip key={item.href} content={item.label} side="right">
                        {link}
                      </Tooltip>
                    );
                  }

                  return link;
                })}
              </div>
            </div>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className={cn("border-t border-gray-100", collapsed ? "px-2 py-3" : "px-2 py-3")}>
        {/* Settings */}
        {collapsed ? (
          <Tooltip content="Settings" side="right">
            <Link
              href={SETTINGS_ITEM.href}
              className={cn(
                "flex items-center justify-center rounded-lg py-2 text-sm transition-colors",
                pathname === SETTINGS_ITEM.href
                  ? "bg-coral/5 text-coral"
                  : "text-gray-400 hover:bg-gray-50 hover:text-gray-600"
              )}
            >
              <SETTINGS_ITEM.icon className="h-[18px] w-[18px]" />
            </Link>
          </Tooltip>
        ) : (
          <Link
            href={SETTINGS_ITEM.href}
            className={cn(
              "flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors",
              pathname === SETTINGS_ITEM.href
                ? "bg-coral/5 text-coral border-l-2 border-coral -ml-px"
                : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            )}
          >
            <SETTINGS_ITEM.icon
              className={cn(
                "h-[18px] w-[18px]",
                pathname === SETTINGS_ITEM.href ? "text-coral" : "text-gray-400"
              )}
            />
            <span>Settings</span>
          </Link>
        )}

        {/* User info + sign out */}
        {!collapsed && user && (
          <div className="mt-2 flex items-center gap-2 rounded-lg px-2.5 py-2">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-medium text-gray-600">
              {user.full_name?.charAt(0)?.toUpperCase() || "U"}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium text-gray-700 truncate">{user.full_name}</p>
              <p className="text-[10px] text-gray-400 truncate">{user.email}</p>
            </div>
            <button
              onClick={onLogout}
              className="text-[10px] text-gray-400 hover:text-red-500 transition-colors"
            >
              Sign out
            </button>
          </div>
        )}

        {/* Collapsed: sign out icon */}
        {collapsed && (
          <Tooltip content="Sign out" side="right">
            <button
              onClick={onLogout}
              className="mt-1 flex w-full items-center justify-center rounded-lg py-2 text-gray-400 hover:bg-red-50 hover:text-red-500 transition-colors"
            >
              <LogOut className="h-[18px] w-[18px]" />
            </button>
          </Tooltip>
        )}

        {/* Collapse toggle */}
        <button
          onClick={onToggle}
          className="mt-1 flex w-full items-center justify-center rounded-lg py-1.5 text-gray-400 hover:bg-gray-50 hover:text-gray-600 transition-colors"
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
    </aside>
  );
}
