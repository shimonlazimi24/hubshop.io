"use client";

import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Calendar, CheckCircle, Clock } from "lucide-react";
import { getCalendar, type CalendarEntry } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { useWorkspace } from "@/hooks/useWorkspace";


const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export default function ContentCalendarPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [entries, setEntries] = useState<CalendarEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAccessToken();
    if (!token || !WORKSPACE_ID) return;
    setLoading(true);
    getCalendar(WORKSPACE_ID, year, month, token)
      .then(setEntries)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [year, month]);

  function prevMonth() {
    if (month === 1) { setMonth(12); setYear(y => y - 1); }
    else setMonth(m => m - 1);
  }

  function nextMonth() {
    if (month === 12) { setMonth(1); setYear(y => y + 1); }
    else setMonth(m => m + 1);
  }

  const entryMap = new Map(entries.map(e => [e.date, e]));
  const firstDay = new Date(year, month - 1, 1).getDay();
  const daysInMonth = new Date(year, month, 0).getDate();
  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  const totalScheduled = entries.filter(e => e.video_count > 0).length;
  const totalVideos = entries.reduce((s, e) => s + e.video_count, 0);

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Days with Content"
            value={totalScheduled}
            icon={Calendar}
            iconColor="text-coral"
            loading={loading}
          />
          <MetricCard
            label="Videos This Month"
            value={totalVideos}
            icon={CheckCircle}
            iconColor="text-success"
            loading={loading}
          />
          <MetricCard
            label="Publishing Consistency"
            value={daysInMonth > 0 ? `${Math.round((totalScheduled / daysInMonth) * 100)}%` : "0%"}
            icon={Clock}
            iconColor="text-info"
            loading={loading}
          />
        </MetricBar>
      }
    >
      <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] overflow-hidden">
        {/* Month navigation */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <button
            onClick={prevMonth}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <h3 className="text-sm font-semibold text-gray-900">
            {MONTH_NAMES[month - 1]} {year}
          </h3>
          <button
            onClick={nextMonth}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>

        {/* Day headers */}
        <div className="grid grid-cols-7 border-b border-gray-100">
          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(d => (
            <div key={d} className="px-2 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider text-center">
              {d}
            </div>
          ))}
        </div>

        {/* Calendar grid */}
        <div className="grid grid-cols-7">
          {Array.from({ length: firstDay }).map((_, i) => (
            <div key={`empty-${i}`} className="min-h-[80px] border-b border-r border-gray-50" />
          ))}
          {days.map(day => {
            const dateStr = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
            const entry = entryMap.get(dateStr);
            const isToday = day === now.getDate() && month === now.getMonth() + 1 && year === now.getFullYear();
            return (
              <div key={day} className="min-h-[80px] border-b border-r border-gray-50 p-1.5">
                <span className={`inline-flex h-6 w-6 items-center justify-center rounded-full text-xs ${isToday ? "bg-coral text-white font-semibold" : "text-gray-400"}`}>
                  {day}
                </span>
                {entry && entry.video_count > 0 && (
                  <div className="mt-1">
                    <span className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-medium rounded-md bg-coral/10 text-coral">
                      {entry.video_count} video{entry.video_count > 1 ? "s" : ""}
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {loading && <div className="text-center py-4 text-gray-500 text-sm mt-4">Loading calendar...</div>}
    </PageShell>
  );
}
