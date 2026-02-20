"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Bell,
  Info,
  AlertTriangle,
  XCircle,
  CheckCircle2,
  CheckCheck,
  Filter,
} from "lucide-react";
import { getAccessToken } from "@/lib/auth";
import {
  listNotifications,
  markNotificationRead,
  markAllNotificationsRead,
  getNotificationPreferences,
  updateNotificationPreference,
  type NotificationItem,
  type NotificationPref,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const MODULE_FILTERS = [
  { value: "", label: "All Modules" },
  { value: "commerce", label: "Commerce" },
  { value: "advertising", label: "Advertising" },
  { value: "content", label: "Content" },
  { value: "creators", label: "Creators" },
];

const NOTIFICATION_ICONS: Record<
  string,
  { icon: typeof Info; color: string; bg: string }
> = {
  INFO: { icon: Info, color: "text-blue-500", bg: "bg-blue-50" },
  WARNING: { icon: AlertTriangle, color: "text-yellow-500", bg: "bg-yellow-50" },
  ERROR: { icon: XCircle, color: "text-red-500", bg: "bg-red-50" },
  SUCCESS: { icon: CheckCircle2, color: "text-green-500", bg: "bg-green-50" },
};

const PREF_MODULES = ["commerce", "advertising", "content", "creators"];
const PREF_CHANNELS = ["email", "in_app", "webhook"];

function formatTimestamp(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "unread">("all");
  const [moduleFilter, setModuleFilter] = useState("");
  const [preferences, setPreferences] = useState<NotificationPref[]>([]);
  const [prefsLoading, setPrefsLoading] = useState(true);

  const fetchNotifications = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const params: { is_read?: boolean; module?: string } = {};
      if (filter === "unread") params.is_read = false;
      if (moduleFilter) params.module = moduleFilter;
      const data = await listNotifications(WORKSPACE_ID, token, params);
      setNotifications(data.items);
    } catch {
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  }, [filter, moduleFilter]);

  const fetchPreferences = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setPrefsLoading(false);
      return;
    }
    try {
      const data = await getNotificationPreferences(token);
      setPreferences(data);
    } catch {
      setPreferences([]);
    } finally {
      setPrefsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  async function handleMarkRead(notificationId: string) {
    const token = getAccessToken();
    if (!token) return;
    try {
      const updated = await markNotificationRead(notificationId, token);
      setNotifications((prev) =>
        prev.map((n) => (n.id === updated.id ? updated : n))
      );
    } catch {
      // Silent fail
    }
  }

  async function handleMarkAllRead() {
    const token = getAccessToken();
    if (!token) return;
    try {
      await markAllNotificationsRead(WORKSPACE_ID, token);
      setNotifications((prev) =>
        prev.map((n) => ({
          ...n,
          is_read: true,
          read_at: new Date().toISOString(),
        }))
      );
    } catch {
      // Silent fail
    }
  }

  async function handleTogglePref(
    module: string,
    channel: string,
    currentEnabled: boolean
  ) {
    const token = getAccessToken();
    if (!token) return;
    try {
      const updated = await updateNotificationPreference(
        { module, channel, is_enabled: !currentEnabled },
        token
      );
      setPreferences((prev) => {
        const existing = prev.findIndex(
          (p) => p.module === module && p.channel === channel
        );
        if (existing >= 0) {
          const copy = [...prev];
          copy[existing] = updated;
          return copy;
        }
        return [...prev, updated];
      });
    } catch {
      // Silent fail
    }
  }

  function isPrefEnabled(module: string, channel: string): boolean {
    const pref = preferences.find(
      (p) => p.module === module && p.channel === channel
    );
    return pref?.is_enabled ?? false;
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div className="max-w-6xl">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-6">
        <div className="flex items-center gap-2">
          {/* All / Unread tabs */}
          <div className="flex rounded-lg border border-gray-200 overflow-hidden">
            <button
              onClick={() => setFilter("all")}
              className={cn(
                "px-3 py-1.5 text-xs font-medium transition-colors",
                filter === "all"
                  ? "bg-coral text-white"
                  : "bg-white text-gray-500 hover:bg-gray-50"
              )}
            >
              All
            </button>
            <button
              onClick={() => setFilter("unread")}
              className={cn(
                "px-3 py-1.5 text-xs font-medium transition-colors",
                filter === "unread"
                  ? "bg-coral text-white"
                  : "bg-white text-gray-500 hover:bg-gray-50"
              )}
            >
              Unread
              {unreadCount > 0 && (
                <span className="ml-1.5 inline-flex items-center justify-center rounded-full bg-coral/20 px-1.5 text-[10px] font-semibold text-coral">
                  {unreadCount}
                </span>
              )}
            </button>
          </div>

          {/* Module filter */}
          <div className="flex items-center gap-1.5">
            <Filter className="h-3.5 w-3.5 text-gray-400" />
            <select
              value={moduleFilter}
              onChange={(e) => setModuleFilter(e.target.value)}
              className="rounded-lg border border-gray-200 px-2 py-1.5 text-xs text-gray-600 focus:border-coral focus:ring-1 focus:ring-coral outline-none bg-white"
            >
              {MODULE_FILTERS.map((mf) => (
                <option key={mf.value} value={mf.value}>
                  {mf.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleMarkAllRead}
          disabled={unreadCount === 0}
          className="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <CheckCheck className="h-3.5 w-3.5" />
          Mark All Read
        </button>
      </div>

      {/* Notification List */}
      <div className="rounded-xl border border-gray-100 bg-white mb-8">
        {loading ? (
          <div className="p-4 space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-start gap-3 py-3">
                <Skeleton className="h-8 w-8 rounded-lg flex-shrink-0" />
                <div className="flex-1">
                  <Skeleton className="h-4 w-48 mb-2" />
                  <Skeleton className="h-3 w-72" />
                </div>
                <Skeleton className="h-3 w-12" />
              </div>
            ))}
          </div>
        ) : notifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 px-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-50 mb-3">
              <Bell className="h-5 w-5 text-gray-300" />
            </div>
            <p className="text-sm text-gray-400">No notifications</p>
            <p className="text-xs text-gray-300 mt-1">
              {filter === "unread"
                ? "All caught up!"
                : "Notifications will appear here as events happen"}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {notifications.map((notification) => {
              const typeInfo =
                NOTIFICATION_ICONS[notification.notification_type] ||
                NOTIFICATION_ICONS.INFO;
              const Icon = typeInfo.icon;
              return (
                <button
                  key={notification.id}
                  onClick={() => {
                    if (!notification.is_read) handleMarkRead(notification.id);
                  }}
                  className={cn(
                    "w-full flex items-start gap-3 px-4 py-3.5 text-left hover:bg-gray-50/50 transition-colors",
                    !notification.is_read && "bg-coral/[0.02]"
                  )}
                >
                  <div
                    className={cn(
                      "flex h-8 w-8 items-center justify-center rounded-lg flex-shrink-0",
                      typeInfo.bg
                    )}
                  >
                    <Icon className={cn("h-4 w-4", typeInfo.color)} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p
                        className={cn(
                          "text-sm",
                          notification.is_read
                            ? "text-gray-600"
                            : "font-medium text-gray-900"
                        )}
                      >
                        {notification.title}
                      </p>
                      {!notification.is_read && (
                        <span className="h-1.5 w-1.5 rounded-full bg-coral flex-shrink-0" />
                      )}
                    </div>
                    <p className="text-xs text-gray-400 mt-0.5 line-clamp-2">
                      {notification.message}
                    </p>
                    {notification.module && (
                      <span className="inline-flex items-center rounded-md bg-gray-50 px-1.5 py-0.5 text-[10px] font-medium text-gray-500 mt-1.5">
                        {notification.module}
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] text-gray-300 flex-shrink-0 pt-0.5">
                    {formatTimestamp(notification.created_at)}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Notification Preferences */}
      <div>
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Notification Preferences
        </h2>
        <div className="rounded-xl border border-gray-100 bg-white overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left text-xs font-medium text-gray-400 px-4 py-3">
                    Module
                  </th>
                  {PREF_CHANNELS.map((channel) => (
                    <th
                      key={channel}
                      className="text-center text-xs font-medium text-gray-400 px-4 py-3"
                    >
                      {channel === "in_app"
                        ? "In-App"
                        : channel.charAt(0).toUpperCase() + channel.slice(1)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {prefsLoading ? (
                  Array.from({ length: 4 }).map((_, i) => (
                    <tr key={i} className="border-b border-gray-50">
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-24" />
                      </td>
                      {PREF_CHANNELS.map((ch) => (
                        <td key={ch} className="px-4 py-3 text-center">
                          <Skeleton className="h-5 w-9 mx-auto rounded-full" />
                        </td>
                      ))}
                    </tr>
                  ))
                ) : (
                  PREF_MODULES.map((mod) => (
                    <tr
                      key={mod}
                      className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors"
                    >
                      <td className="px-4 py-3 text-sm font-medium text-gray-700 capitalize">
                        {mod}
                      </td>
                      {PREF_CHANNELS.map((channel) => {
                        const enabled = isPrefEnabled(mod, channel);
                        return (
                          <td key={channel} className="px-4 py-3 text-center">
                            <button
                              onClick={() =>
                                handleTogglePref(mod, channel, enabled)
                              }
                              className={cn(
                                "relative inline-flex h-5 w-9 items-center rounded-full transition-colors",
                                enabled ? "bg-coral" : "bg-gray-200"
                              )}
                            >
                              <span
                                className={cn(
                                  "inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform",
                                  enabled ? "translate-x-[18px]" : "translate-x-[3px]"
                                )}
                              />
                            </button>
                          </td>
                        );
                      })}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
