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
  FileText,
  Calendar,
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
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { Modal } from "@/components/ui/modal";
import { StatusBadge } from "@/components/ui/status-badge";
import { toast } from "@/lib/toast-store";
import { Skeleton } from "@/components/ui/skeleton";
import { useWorkspace } from "@/hooks/useWorkspace";


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
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
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
    if (!token || !WORKSPACE_ID) {
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
    if (!token || !WORKSPACE_ID || !formName.trim()) return;
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
      toast.success("Report created successfully");
      setShowCreate(false);
      resetForm();
      fetchReports();
    } catch {
      toast.error("Failed to create report");
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
    if (!token || !WORKSPACE_ID) return;
    try {
      await generateReport(reportId, token);
      toast.success("Report generation started");
      fetchReports();
    } catch {
      toast.error("Failed to generate report");
    }
  }

  async function handleDelete(reportId: string) {
    const token = getAccessToken();
    if (!token || !WORKSPACE_ID) return;
    try {
      await deleteScheduledReport(reportId, token);
      toast.success("Report deleted");
      fetchReports();
    } catch {
      toast.error("Failed to delete report");
    }
  }

  function toggleModule(mod: string) {
    setFormModules((prev) =>
      prev.includes(mod) ? prev.filter((m) => m !== mod) : [...prev, mod]
    );
  }

  const activeReports = reports.filter((r) => r.is_active).length;

  const columns: Column<ScheduledReportSummary>[] = [
    {
      key: "name",
      header: "Name",
      render: (row) => (
        <div>
          <p className="text-sm font-medium text-gray-900">{row.name}</p>
          {row.description && <p className="text-xs text-gray-400 mt-0.5">{row.description}</p>}
        </div>
      ),
    },
    {
      key: "frequency",
      header: "Frequency",
      className: "w-28",
      render: (row) => (
        <span className="inline-flex items-center rounded-md bg-gray-50 px-2 py-0.5 text-xs font-medium text-gray-600">
          {row.frequency}
        </span>
      ),
    },
    {
      key: "format",
      header: "Format",
      className: "w-20",
      render: (row) => <span className="text-sm text-gray-600">{row.format}</span>,
    },
    {
      key: "active",
      header: "Active",
      className: "w-20",
      render: (row) =>
        row.is_active ? (
          <StatusBadge variant="active" label="Active" />
        ) : (
          <StatusBadge variant="paused" label="Inactive" />
        ),
    },
    {
      key: "last_run",
      header: "Last Run",
      render: (row) => <span className="text-xs text-gray-500">{formatDate(row.last_run_at)}</span>,
    },
    {
      key: "actions",
      header: "Actions",
      className: "w-24",
      render: (row) => (
        <div className="flex items-center justify-end gap-1">
          <button
            onClick={() => handleGenerate(row.id)}
            className="rounded-lg p-1.5 text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 transition-colors"
            title="Generate now"
          >
            <Play className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => handleDelete(row.id)}
            className="rounded-lg p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
            title="Delete"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      ),
    },
  ];

  return (
    <PageShell
      header={
        loading ? (
          <MetricBar>
            <Skeleton className="h-16 flex-1 rounded-xl" />
            <Skeleton className="h-16 flex-1 rounded-xl" />
            <Skeleton className="h-16 flex-1 rounded-xl" />
          </MetricBar>
        ) : (
          <MetricBar>
            <MetricCard label="Total Reports" value={reports.length} icon={FileText} />
            <MetricCard label="Active Reports" value={activeReports} icon={CheckCircle2} />
            <MetricCard label="Scheduled" value={reports.filter((r) => r.is_active).length} icon={Calendar} />
          </MetricBar>
        )
      }
      aside={
        <InsightPanel>
          <InsightItem
            title="Automated reporting"
            description="Scheduled reports run automatically and deliver data in your chosen format."
            variant="success"
          />
          <InsightItem
            title="Tip"
            description="Use weekly CSV reports for regular business reviews. Monthly reports work best for executive summaries."
          />
        </InsightPanel>
      }
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Scheduled Reports</h3>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
        >
          <Plus className="h-3.5 w-3.5" />
          Create Report
        </button>
      </div>

      <DataTable
        columns={columns}
        data={reports}
        keyExtractor={(row) => row.id}
        emptyTitle="No scheduled reports"
        emptyDescription="Create one to automate your analytics delivery"
        emptyAction={{ label: "Create Report", onClick: () => setShowCreate(true) }}
      />

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 px-1">
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

      {/* Create Modal */}
      <Modal open={showCreate} onClose={() => { setShowCreate(false); resetForm(); }} title="New Scheduled Report">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Name *</label>
              <input
                type="text"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="Weekly Commerce Summary"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-coral focus:ring-1 focus:ring-coral outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
              <input
                type="text"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                placeholder="Optional description"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-coral focus:ring-1 focus:ring-coral outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-2">Modules</label>
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

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Frequency</label>
              <select
                value={formFrequency}
                onChange={(e) => setFormFrequency(e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-coral focus:ring-1 focus:ring-coral outline-none bg-white"
              >
                {FREQUENCY_OPTIONS.map((f) => (
                  <option key={f} value={f}>{f}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Format</label>
              <select
                value={formFormat}
                onChange={(e) => setFormFormat(e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-coral focus:ring-1 focus:ring-coral outline-none bg-white"
              >
                {FORMAT_OPTIONS.map((f) => (
                  <option key={f} value={f}>{f}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              onClick={() => { setShowCreate(false); resetForm(); }}
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
      </Modal>
    </PageShell>
  );
}
