"use client";

import { useState } from "react";
import {
  UserPlus,
  FileText,
  Download,
  ClipboardCheck,
  Plus,
  X,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  AlertTriangle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";

interface LeadForm {
  id: string;
  name: string;
  status: "active" | "paused" | "draft";
  leads: number;
  conversionRate: number;
  createdAt: string;
  lastSubmission: string | null;
}

const MOCK_FORMS: LeadForm[] = [
  { id: "lf-1", name: "Product Interest Survey", status: "active", leads: 1_240, conversionRate: 8.4, createdAt: "2026-01-10", lastSubmission: "2026-02-20T09:30:00Z" },
  { id: "lf-2", name: "Newsletter Signup", status: "active", leads: 890, conversionRate: 12.1, createdAt: "2026-01-15", lastSubmission: "2026-02-20T08:15:00Z" },
  { id: "lf-3", name: "Free Trial Request", status: "active", leads: 456, conversionRate: 5.7, createdAt: "2026-01-20", lastSubmission: "2026-02-19T22:00:00Z" },
  { id: "lf-4", name: "Webinar Registration", status: "active", leads: 178, conversionRate: 15.3, createdAt: "2026-02-01", lastSubmission: "2026-02-20T07:45:00Z" },
  { id: "lf-5", name: "Discount Code Claim", status: "active", leads: 67, conversionRate: 22.8, createdAt: "2026-02-10", lastSubmission: "2026-02-19T18:30:00Z" },
  { id: "lf-6", name: "Contest Entry Form", status: "active", leads: 16, conversionRate: 3.2, createdAt: "2026-02-18", lastSubmission: "2026-02-20T10:00:00Z" },
  { id: "lf-7", name: "Summer Campaign (Draft)", status: "draft", leads: 0, conversionRate: 0, createdAt: "2026-02-19", lastSubmission: null },
];

interface DownloadTask {
  id: string;
  formName: string;
  dateRange: string;
  recordCount: number;
  status: "ready" | "processing" | "expired";
  createdAt: string;
}

const MOCK_DOWNLOADS: DownloadTask[] = [
  { id: "dl-1", formName: "Product Interest Survey", dateRange: "Feb 1 - Feb 20", recordCount: 342, status: "ready", createdAt: "2026-02-20T06:00:00Z" },
  { id: "dl-2", formName: "Newsletter Signup", dateRange: "Jan 15 - Feb 15", recordCount: 780, status: "processing", createdAt: "2026-02-20T09:00:00Z" },
  { id: "dl-3", formName: "All Forms", dateRange: "Jan 1 - Jan 31", recordCount: 1_450, status: "ready", createdAt: "2026-02-01T12:00:00Z" },
];

export default function LeadsPage() {
  const [showTestLead, setShowTestLead] = useState(false);
  const [testFormId, setTestFormId] = useState("");
  const [testEmail, setTestEmail] = useState("");

  const activeForms = MOCK_FORMS.filter((f) => f.status !== "draft");

  const formColumns: Column<LeadForm>[] = [
    {
      key: "name",
      header: "Form",
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-2">
          <FileText className={cn("h-4 w-4", row.status === "active" ? "text-success" : row.status === "paused" ? "text-warning" : "text-gray-300")} />
          <span className="text-sm font-medium text-gray-900">{row.name}</span>
        </div>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (row) => <StatusBadge variant={row.status === "active" ? "active" : row.status === "paused" ? "paused" : "draft"} label={row.status === "active" ? "Active" : row.status === "paused" ? "Paused" : "Draft"} />,
    },
    {
      key: "leads",
      header: "Leads",
      sortable: true,
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.leads.toLocaleString()}</span>,
    },
    {
      key: "conversionRate",
      header: "Conv. Rate",
      sortable: true,
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{row.conversionRate > 0 ? `${row.conversionRate}%` : "-"}</span>,
    },
    {
      key: "lastSubmission",
      header: "Last Submission",
      render: (row) => <span className="text-sm text-gray-500">{row.lastSubmission ? new Date(row.lastSubmission).toLocaleDateString() : "-"}</span>,
    },
  ];

  return (
    <>
      <PageHeader title="Lead Generation" description="Manage lead forms, downloads, and test submissions" />
      <PageShell
        header={
          <MetricBar>
            <MetricCard label="Total Leads" value="2,847" icon={UserPlus} iconColor="text-purple" trend={{ value: 18.3, direction: "up", label: "vs last month" }} sparklineData={[180, 220, 280, 320, 350, 410, 480]} />
            <MetricCard label="Forms Active" value={6} icon={FileText} iconColor="text-success" />
            <MetricCard label="Download Tasks" value={3} icon={Download} iconColor="text-info" />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="Best Converter"
              description="'Discount Code Claim' has the highest conversion rate at 22.8%."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Low Performer"
              description="'Contest Entry Form' has only 3.2% conversion rate. Consider revising the form."
              variant="warning"
              action={{ label: "Edit form", onClick: () => {} }}
            />
          </InsightPanel>
        }
      >
        {/* Lead Forms */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">Lead Forms</h2>
          <DataTable
            columns={formColumns}
            data={MOCK_FORMS}
            keyExtractor={(row) => row.id}
            emptyTitle="No lead forms found"
          />
        </div>

        {/* Lead Download Queue */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">Lead Downloads</h2>
          <div className="space-y-3">
            {MOCK_DOWNLOADS.map((task) => (
              <div
                key={task.id}
                className="rounded-xl border border-gray-100 bg-white p-5 flex items-center justify-between shadow-[var(--shadow-card)]"
              >
                <div className="flex items-center gap-3">
                  <div className={cn("flex h-9 w-9 items-center justify-center rounded-lg", task.status === "ready" ? "bg-success/10" : task.status === "processing" ? "bg-info/10" : "bg-gray-50")}>
                    {task.status === "ready" ? <CheckCircle className="h-[18px] w-[18px] text-success" /> : task.status === "processing" ? <Clock className="h-[18px] w-[18px] text-info" /> : <AlertCircle className="h-[18px] w-[18px] text-gray-400" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{task.formName}</p>
                    <p className="text-xs text-gray-500">{task.dateRange} | {task.recordCount.toLocaleString()} records</p>
                  </div>
                </div>
                <button
                  disabled={task.status !== "ready"}
                  className={cn("flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors", task.status === "ready" ? "bg-gray-900 text-white hover:bg-gray-800" : "bg-gray-100 text-gray-400 cursor-not-allowed")}
                >
                  <Download className="h-3.5 w-3.5" />
                  {task.status === "processing" ? "Processing..." : task.status === "expired" ? "Expired" : "Download CSV"}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Test Lead Creator */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-gray-900">Test Lead</h2>
            <button
              onClick={() => setShowTestLead(!showTestLead)}
              className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
            >
              {showTestLead ? <X className="h-4 w-4" /> : <ClipboardCheck className="h-4 w-4" />}
              {showTestLead ? "Cancel" : "Create Test Lead"}
            </button>
          </div>
          {showTestLead && (
            <div className="rounded-xl border border-gray-100 bg-white p-5">
              <p className="text-xs text-gray-500 mb-3">Submit a test lead to verify your form integration is working correctly.</p>
              <div className="space-y-3">
                <select value={testFormId} onChange={(e) => setTestFormId(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral">
                  <option value="">Select a form</option>
                  {activeForms.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
                </select>
                <input type="email" value={testEmail} onChange={(e) => setTestEmail(e.target.value)} placeholder="Test email address" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral" />
                <button disabled={!testFormId || !testEmail.trim()} className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 disabled:opacity-50 transition-colors">Submit Test Lead</button>
              </div>
            </div>
          )}
        </div>
      </PageShell>
    </>
  );
}
