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
} from "lucide-react";
import { cn } from "@/lib/utils";

const KPI_CARDS = [
  {
    label: "Total Leads",
    value: 2_847,
    icon: UserPlus,
    color: "text-purple bg-purple/5 border-purple/10",
    iconColor: "text-purple",
  },
  {
    label: "Forms Active",
    value: 6,
    icon: FileText,
    color: "text-emerald-600 bg-emerald-50 border-emerald-100",
    iconColor: "text-emerald-500",
  },
  {
    label: "Download Tasks",
    value: 3,
    icon: Download,
    color: "text-blue-600 bg-blue-50 border-blue-100",
    iconColor: "text-blue-500",
  },
];

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
  {
    id: "lf-1",
    name: "Product Interest Survey",
    status: "active",
    leads: 1_240,
    conversionRate: 8.4,
    createdAt: "2026-01-10",
    lastSubmission: "2026-02-20T09:30:00Z",
  },
  {
    id: "lf-2",
    name: "Newsletter Signup",
    status: "active",
    leads: 890,
    conversionRate: 12.1,
    createdAt: "2026-01-15",
    lastSubmission: "2026-02-20T08:15:00Z",
  },
  {
    id: "lf-3",
    name: "Free Trial Request",
    status: "active",
    leads: 456,
    conversionRate: 5.7,
    createdAt: "2026-01-20",
    lastSubmission: "2026-02-19T22:00:00Z",
  },
  {
    id: "lf-4",
    name: "Webinar Registration",
    status: "active",
    leads: 178,
    conversionRate: 15.3,
    createdAt: "2026-02-01",
    lastSubmission: "2026-02-20T07:45:00Z",
  },
  {
    id: "lf-5",
    name: "Discount Code Claim",
    status: "active",
    leads: 67,
    conversionRate: 22.8,
    createdAt: "2026-02-10",
    lastSubmission: "2026-02-19T18:30:00Z",
  },
  {
    id: "lf-6",
    name: "Contest Entry Form",
    status: "active",
    leads: 16,
    conversionRate: 3.2,
    createdAt: "2026-02-18",
    lastSubmission: "2026-02-20T10:00:00Z",
  },
  {
    id: "lf-7",
    name: "Summer Campaign (Draft)",
    status: "draft",
    leads: 0,
    conversionRate: 0,
    createdAt: "2026-02-19",
    lastSubmission: null,
  },
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
  {
    id: "dl-1",
    formName: "Product Interest Survey",
    dateRange: "Feb 1 - Feb 20",
    recordCount: 342,
    status: "ready",
    createdAt: "2026-02-20T06:00:00Z",
  },
  {
    id: "dl-2",
    formName: "Newsletter Signup",
    dateRange: "Jan 15 - Feb 15",
    recordCount: 780,
    status: "processing",
    createdAt: "2026-02-20T09:00:00Z",
  },
  {
    id: "dl-3",
    formName: "All Forms",
    dateRange: "Jan 1 - Jan 31",
    recordCount: 1_450,
    status: "ready",
    createdAt: "2026-02-01T12:00:00Z",
  },
];

export default function LeadsPage() {
  const [showTestLead, setShowTestLead] = useState(false);
  const [testFormId, setTestFormId] = useState("");
  const [testEmail, setTestEmail] = useState("");

  const activeForms = MOCK_FORMS.filter((f) => f.status !== "draft");

  return (
    <div className="max-w-6xl">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {KPI_CARDS.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.label}
              className="rounded-xl border border-gray-100 bg-white p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <div
                  className={cn(
                    "flex h-9 w-9 items-center justify-center rounded-lg",
                    card.color
                  )}
                >
                  <Icon className={cn("h-[18px] w-[18px]", card.iconColor)} />
                </div>
              </div>
              <p className="text-2xl font-semibold text-gray-900">
                {card.value.toLocaleString()}
              </p>
              <p className="text-xs text-gray-400 mt-1">{card.label}</p>
            </div>
          );
        })}
      </div>

      {/* Lead Forms */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">Lead Forms</h2>
        <div className="bg-white rounded-lg border border-gray-200">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 text-left">
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Form</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Leads</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Conv. Rate</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Last Submission</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {MOCK_FORMS.map((form) => (
                <tr key={form.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <FileText className={cn(
                        "h-4 w-4",
                        form.status === "active" ? "text-emerald-500" : form.status === "paused" ? "text-yellow-500" : "text-gray-300"
                      )} />
                      <span className="text-sm font-medium text-gray-900">{form.name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={cn(
                        "px-2 py-0.5 text-xs rounded-full",
                        form.status === "active"
                          ? "bg-green-100 text-green-700"
                          : form.status === "paused"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-gray-100 text-gray-600"
                      )}
                    >
                      {form.status === "active" ? "Active" : form.status === "paused" ? "Paused" : "Draft"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {form.leads.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {form.conversionRate > 0 ? `${form.conversionRate}%` : "-"}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {form.lastSubmission
                      ? new Date(form.lastSubmission).toLocaleDateString()
                      : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Lead Download Queue */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">Lead Downloads</h2>
        <div className="space-y-3">
          {MOCK_DOWNLOADS.map((task) => (
            <div
              key={task.id}
              className="rounded-xl border border-gray-100 bg-white p-5 flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <div
                  className={cn(
                    "flex h-9 w-9 items-center justify-center rounded-lg",
                    task.status === "ready"
                      ? "bg-green-50"
                      : task.status === "processing"
                      ? "bg-blue-50"
                      : "bg-gray-50"
                  )}
                >
                  {task.status === "ready" ? (
                    <CheckCircle className="h-[18px] w-[18px] text-green-500" />
                  ) : task.status === "processing" ? (
                    <Clock className="h-[18px] w-[18px] text-blue-500" />
                  ) : (
                    <AlertCircle className="h-[18px] w-[18px] text-gray-400" />
                  )}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{task.formName}</p>
                  <p className="text-xs text-gray-500">
                    {task.dateRange} | {task.recordCount.toLocaleString()} records
                  </p>
                </div>
              </div>
              <button
                disabled={task.status !== "ready"}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                  task.status === "ready"
                    ? "bg-gray-900 text-white hover:bg-gray-800"
                    : "bg-gray-100 text-gray-400 cursor-not-allowed"
                )}
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
            <p className="text-xs text-gray-500 mb-3">
              Submit a test lead to verify your form integration is working correctly.
            </p>
            <div className="space-y-3">
              <select
                value={testFormId}
                onChange={(e) => setTestFormId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="">Select a form</option>
                {activeForms.map((f) => (
                  <option key={f.id} value={f.id}>{f.name}</option>
                ))}
              </select>
              <input
                type="email"
                value={testEmail}
                onChange={(e) => setTestEmail(e.target.value)}
                placeholder="Test email address"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              />
              <button
                disabled={!testFormId || !testEmail.trim()}
                className="px-4 py-2 bg-gray-900 text-white rounded-md text-sm font-medium hover:bg-gray-800 disabled:opacity-50"
              >
                Submit Test Lead
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
