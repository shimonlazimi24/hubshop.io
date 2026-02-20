"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Plus,
  Play,
  Trash2,
  CheckCircle2,
  XCircle,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";
import { getAccessToken } from "@/lib/auth";
import {
  listScheduledReports,
  createScheduledReport,
  generateReport,
  deleteScheduledReport,
  type ScheduledReportSummary,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const FREQUENCY_OPTIONS = ["DAILY", "WEEKLY", "MONTHLY"];
const FORMAT_OPTIONS = ["CSV", "XLSX", "JSON"];
const MODULE_OPTIONS = ["commerce", "advertising", "content", "creators"];

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "\u2014";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ReportsPage() {
  const [reports, setReports] = useState<ScheduledReportSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);

  // Create form state
  const [formName, setFormName] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [formModules, setFormModules] = useState<string[]>([]);
  const [formFrequency, setFormFrequency] = useState("DAILY");
  const [formFormat, setFormFormat] = useState("CSV");

  const fetchReports = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const data = await listScheduledReports(WORKSPACE_ID, token, { page });
      setReports(data.items);
      setTotalPages(data.total_pages);
    } catch {
      setReports([]);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  async function handleCreate() {
    const token = getAccessToken();
    if (!token || !formName.trim()) return;
    setCreating(true);
    try {
      await createScheduledReport(
        WORKSPACE_ID,
        {
          name: formName,
          description: formDescription || undefined,
          modules: formModules,
          frequency: formFrequency,
          format: formFormat,
        },
        token
      );
      setShowCreate(false);
      resetForm();
      fetchReports();
    } catch {
      // Error handling - keep form open
    } finally {
      setCreating(false);
    }
  }

  function resetForm() {
    setFormName("");
    setFormDescription("");
    setFormModules([]);
    setFormFrequency("DAILY");
    setFormFormat("CSV");
  }

  async function handleGenerate(reportId: string) {
    const token = getAccessToken();
    if (!token) return;
    try {
      await generateReport(reportId, token);
      fetchReports();
    } catch {
      // Silent fail
    }
  }

  async function handleDelete(reportId: string) {
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteScheduledReport(reportId, token);
      fetchReports();
    } catch {
      // Silent fail
    }
  }

  function toggleModule(mod: string) {
    setFormModules((prev) =>
      prev.includes(mod) ? prev.filter((m) => m !== mod) : [...prev, mod]
    );
  }

  return (
    <div className="max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-sm font-semibold text-gray-900">
          Scheduled Reports
        </h2>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
        >
          <Plus className="h-3.5 w-3.5" />
          Create Report
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="rounded-xl border border-gray-200 bg-white p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-900">
              New Scheduled Report
            </h3>
            <button
              onClick={() => {
                setShowCreate(false);
                resetForm();
              }}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Name *
              </label>
              <input
                type="text"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="Weekly Commerce Summary"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-coral focus:ring-1 focus:ring-coral outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Description
              </label>
              <input
                type="text"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                placeholder="Optional description"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-coral focus:ring-1 focus:ring-coral outline-none"
              />
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-xs font-medium text-gray-500 mb-2">
              Modules
            </label>
            <div className="flex flex-wrap gap-2">
              {MODULE_OPTIONS.map((mod) => (
                <button
                  key={mod}
                  onClick={() => toggleModule(mod)}
                  className={cn(
                    "rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors",
                    formModules.includes(mod)
                      ? "border-coral bg-coral/5 text-coral"
                      : "border-gray-200 text-gray-500 hover:border-gray-300"
                  )}
                >
                  {mod.charAt(0).toUpperCase() + mod.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Frequency
              </label>
              <select
                value={formFrequency}
                onChange={(e) => setFormFrequency(e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-coral focus:ring-1 focus:ring-coral outline-none bg-white"
              >
                {FREQUENCY_OPTIONS.map((f) => (
                  <option key={f} value={f}>
                    {f}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Format
              </label>
              <select
                value={formFormat}
                onChange={(e) => setFormFormat(e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-coral focus:ring-1 focus:ring-coral outline-none bg-white"
              >
                {FORMAT_OPTIONS.map((f) => (
                  <option key={f} value={f}>
                    {f}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <button
              onClick={() => {
                setShowCreate(false);
                resetForm();
              }}
              className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={!formName.trim() || creating}
              className="rounded-lg bg-coral px-4 py-2 text-sm font-medium text-white hover:bg-coral/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {creating ? "Creating..." : "Create Report"}
            </button>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="rounded-xl border border-gray-100 bg-white overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left text-xs font-medium text-gray-400 px-4 py-3">
                  Name
                </th>
                <th className="text-left text-xs font-medium text-gray-400 px-4 py-3">
                  Frequency
                </th>
                <th className="text-left text-xs font-medium text-gray-400 px-4 py-3">
                  Format
                </th>
                <th className="text-left text-xs font-medium text-gray-400 px-4 py-3">
                  Active
                </th>
                <th className="text-left text-xs font-medium text-gray-400 px-4 py-3">
                  Last Run
                </th>
                <th className="text-right text-xs font-medium text-gray-400 px-4 py-3">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <tr key={i} className="border-b border-gray-50">
                    <td className="px-4 py-3">
                      <Skeleton className="h-4 w-40" />
                    </td>
                    <td className="px-4 py-3">
                      <Skeleton className="h-4 w-16" />
                    </td>
                    <td className="px-4 py-3">
                      <Skeleton className="h-4 w-12" />
                    </td>
                    <td className="px-4 py-3">
                      <Skeleton className="h-4 w-8" />
                    </td>
                    <td className="px-4 py-3">
                      <Skeleton className="h-4 w-28" />
                    </td>
                    <td className="px-4 py-3">
                      <Skeleton className="h-4 w-16 ml-auto" />
                    </td>
                  </tr>
                ))
              ) : reports.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 py-12 text-center text-sm text-gray-400"
                  >
                    No scheduled reports yet. Create one to get started.
                  </td>
                </tr>
              ) : (
                reports.map((report) => (
                  <tr
                    key={report.id}
                    className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors"
                  >
                    <td className="px-4 py-3">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {report.name}
                        </p>
                        {report.description && (
                          <p className="text-xs text-gray-400 mt-0.5">
                            {report.description}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center rounded-md bg-gray-50 px-2 py-0.5 text-xs font-medium text-gray-600">
                        {report.frequency}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-600">
                        {report.format}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {report.is_active ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-gray-300" />
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs text-gray-500">
                        {formatDate(report.last_run_at)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => handleGenerate(report.id)}
                          className="rounded-lg p-1.5 text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 transition-colors"
                          title="Generate now"
                        >
                          <Play className="h-3.5 w-3.5" />
                        </button>
                        <button
                          onClick={() => handleDelete(report.id)}
                          className="rounded-lg p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between border-t border-gray-100 px-4 py-3">
            <p className="text-xs text-gray-400">
              Page {page} of {totalPages}
            </p>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="rounded-lg p-1.5 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="rounded-lg p-1.5 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
