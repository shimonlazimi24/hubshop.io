"use client";

import { useState } from "react";
import { Zap, Plus, Play, Pause, Clock, X, TrendingUp, AlertTriangle } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar } from "@/components/ui/filter-bar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";
import { ActionMenu } from "@/components/ui/action-menu";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";
import { toast } from "@/lib/toast-store";

interface AutomatedRule {
  id: string;
  name: string;
  condition_summary: string;
  action_summary: string;
  status: "active" | "paused";
  last_triggered: string | null;
  trigger_count: number;
  created_at: string;
}

const MOCK_RULES: AutomatedRule[] = [
  { id: "rule-1", name: "Pause Low ROAS Campaigns", condition_summary: "When ROAS < 1.0 for 3 consecutive days", action_summary: "Pause campaign", status: "active", last_triggered: "2026-02-19T14:30:00Z", trigger_count: 5, created_at: "2026-01-15T10:00:00Z" },
  { id: "rule-2", name: "Scale High Performers", condition_summary: "When CTR > 3% and CPA < $5", action_summary: "Increase budget by 20%", status: "active", last_triggered: "2026-02-20T08:00:00Z", trigger_count: 12, created_at: "2026-01-20T09:00:00Z" },
  { id: "rule-3", name: "Alert on Overspend", condition_summary: "When daily spend exceeds budget by 10%", action_summary: "Send notification alert", status: "active", last_triggered: "2026-02-18T22:00:00Z", trigger_count: 3, created_at: "2026-02-01T11:00:00Z" },
  { id: "rule-4", name: "Rotate Creatives", condition_summary: "When ad frequency > 4.0", action_summary: "Switch to next creative set", status: "paused", last_triggered: null, trigger_count: 0, created_at: "2026-02-10T14:00:00Z" },
  { id: "rule-5", name: "Weekend Budget Boost", condition_summary: "On Saturday and Sunday", action_summary: "Increase budget by 30%", status: "active", last_triggered: "2026-02-16T00:00:00Z", trigger_count: 8, created_at: "2026-01-25T16:00:00Z" },
];

export default function AutomationPage() {
  const [rules] = useState<AutomatedRule[]>(MOCK_RULES);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newCondition, setNewCondition] = useState("");
  const [newAction, setNewAction] = useState("");
  const [search, setSearch] = useState("");

  function handleCreate() {
    if (!newName.trim() || !newCondition.trim() || !newAction.trim()) return;
    toast.success("Rule created successfully");
    setNewName("");
    setNewCondition("");
    setNewAction("");
    setShowCreate(false);
  }

  const activeCount = rules.filter((r) => r.status === "active").length;

  const filtered = rules.filter((r) => {
    if (search && !r.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const columns: Column<AutomatedRule>[] = [
    {
      key: "name",
      header: "Rule",
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-2">
          <Zap className={`h-4 w-4 ${row.status === "active" ? "text-warning" : "text-gray-300"}`} />
          <div>
            <p className="text-sm font-medium text-gray-900">{row.name}</p>
            <p className="text-xs text-gray-500">{row.action_summary}</p>
          </div>
        </div>
      ),
    },
    {
      key: "condition",
      header: "Condition",
      render: (row) => <span className="text-sm text-gray-600">{row.condition_summary}</span>,
    },
    {
      key: "status",
      header: "Status",
      render: (row) => (
        <StatusBadge variant={row.status === "active" ? "active" : "paused"} label={row.status === "active" ? "Active" : "Paused"} />
      ),
    },
    {
      key: "last_triggered",
      header: "Last Triggered",
      sortable: true,
      render: (row) => (
        row.last_triggered ? (
          <div className="flex items-center gap-1.5">
            <Clock className="h-3.5 w-3.5 text-gray-400" />
            <span className="text-sm text-gray-500">{new Date(row.last_triggered).toLocaleDateString()}</span>
            <span className="text-xs text-gray-400 tabular-nums">({row.trigger_count}x)</span>
          </div>
        ) : (
          <span className="text-sm text-gray-400">Never</span>
        )
      ),
    },
    {
      key: "actions",
      header: "",
      className: "w-12",
      render: (row) => (
        <ActionMenu
          items={[
            { label: row.status === "active" ? "Pause" : "Activate", icon: row.status === "active" ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />, onClick: () => toast.info("Toggle coming soon") },
            { label: "Delete", icon: <X className="h-4 w-4" />, onClick: () => toast.info("Delete coming soon"), variant: "danger" },
          ]}
        />
      ),
    },
  ];

  return (
    <>
      <PageHeader
        title="Automation Rules"
        description="Automated campaign management rules and triggers"
        actions={
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
          >
            {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            {showCreate ? "Cancel" : "Create Rule"}
          </button>
        }
      />
      <PageShell
        header={
          <MetricBar>
            <MetricCard label="Active Rules" value={activeCount} icon={Zap} iconColor="text-warning" />
            <MetricCard label="Total Rules" value={rules.length} icon={Zap} iconColor="text-purple" />
            <MetricCard label="Triggers Today" value={3} icon={Play} iconColor="text-info" trend={{ value: 50, direction: "up", label: "vs yesterday" }} />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="Top Rule"
              description="'Scale High Performers' has triggered 12 times, saving an estimated 4 hours of manual work."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Paused Rule"
              description="'Rotate Creatives' is paused and has never triggered. Consider activating or removing."
              variant="warning"
            />
          </InsightPanel>
        }
      >
        <FilterBar searchValue={search} onSearchChange={setSearch} searchPlaceholder="Search rules..." />

        {showCreate && (
          <div className="rounded-xl border border-gray-100 bg-white p-5 mb-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">New Automated Rule</h3>
            <div className="space-y-3">
              <input type="text" value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Rule name" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral" />
              <input type="text" value={newCondition} onChange={(e) => setNewCondition(e.target.value)} placeholder="Condition (e.g., When ROAS < 1.0)" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral" />
              <input type="text" value={newAction} onChange={(e) => setNewAction(e.target.value)} placeholder="Action (e.g., Pause campaign)" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral" />
              <button onClick={handleCreate} disabled={!newName.trim() || !newCondition.trim() || !newAction.trim()} className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 disabled:opacity-50 transition-colors">Create Rule</button>
            </div>
          </div>
        )}

        <DataTable
          columns={columns}
          data={filtered}
          keyExtractor={(row) => row.id}
          emptyTitle="No automation rules"
          emptyDescription="Create your first automation rule to optimize campaigns automatically."
        />
      </PageShell>
    </>
  );
}
