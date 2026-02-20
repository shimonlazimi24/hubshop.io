"use client";

import { useState } from "react";
import { Zap, Plus, Play, Pause, Clock, AlertTriangle, X } from "lucide-react";
import { cn } from "@/lib/utils";

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
  {
    id: "rule-1",
    name: "Pause Low ROAS Campaigns",
    condition_summary: "When ROAS < 1.0 for 3 consecutive days",
    action_summary: "Pause campaign",
    status: "active",
    last_triggered: "2026-02-19T14:30:00Z",
    trigger_count: 5,
    created_at: "2026-01-15T10:00:00Z",
  },
  {
    id: "rule-2",
    name: "Scale High Performers",
    condition_summary: "When CTR > 3% and CPA < $5",
    action_summary: "Increase budget by 20%",
    status: "active",
    last_triggered: "2026-02-20T08:00:00Z",
    trigger_count: 12,
    created_at: "2026-01-20T09:00:00Z",
  },
  {
    id: "rule-3",
    name: "Alert on Overspend",
    condition_summary: "When daily spend exceeds budget by 10%",
    action_summary: "Send notification alert",
    status: "active",
    last_triggered: "2026-02-18T22:00:00Z",
    trigger_count: 3,
    created_at: "2026-02-01T11:00:00Z",
  },
  {
    id: "rule-4",
    name: "Rotate Creatives",
    condition_summary: "When ad frequency > 4.0",
    action_summary: "Switch to next creative set",
    status: "paused",
    last_triggered: null,
    trigger_count: 0,
    created_at: "2026-02-10T14:00:00Z",
  },
  {
    id: "rule-5",
    name: "Weekend Budget Boost",
    condition_summary: "On Saturday and Sunday",
    action_summary: "Increase budget by 30%",
    status: "active",
    last_triggered: "2026-02-16T00:00:00Z",
    trigger_count: 8,
    created_at: "2026-01-25T16:00:00Z",
  },
];

export default function AutomationPage() {
  const [rules] = useState<AutomatedRule[]>(MOCK_RULES);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newCondition, setNewCondition] = useState("");
  const [newAction, setNewAction] = useState("");

  function handleCreate() {
    if (!newName.trim() || !newCondition.trim() || !newAction.trim()) return;
    // Placeholder: would call API to create rule
    setNewName("");
    setNewCondition("");
    setNewAction("");
    setShowCreate(false);
  }

  const activeCount = rules.filter((r) => r.status === "active").length;

  return (
    <div className="max-w-6xl">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">
          {activeCount} active rule{activeCount !== 1 ? "s" : ""} of {rules.length} total
        </p>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
        >
          {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showCreate ? "Cancel" : "Create Rule"}
        </button>
      </div>

      {showCreate && (
        <div className="rounded-xl border border-gray-100 bg-white p-5 mb-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">New Automated Rule</h3>
          <div className="space-y-3">
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Rule name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <input
              type="text"
              value={newCondition}
              onChange={(e) => setNewCondition(e.target.value)}
              placeholder="Condition (e.g., When ROAS < 1.0)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <input
              type="text"
              value={newAction}
              onChange={(e) => setNewAction(e.target.value)}
              placeholder="Action (e.g., Pause campaign)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <button
              onClick={handleCreate}
              disabled={!newName.trim() || !newCondition.trim() || !newAction.trim()}
              className="px-4 py-2 bg-gray-900 text-white rounded-md text-sm font-medium hover:bg-gray-800 disabled:opacity-50"
            >
              Create Rule
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Rule</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Condition</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Last Triggered</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {rules.map((rule) => (
              <tr key={rule.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Zap className={cn("h-4 w-4", rule.status === "active" ? "text-yellow-500" : "text-gray-300")} />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{rule.name}</p>
                      <p className="text-xs text-gray-500">{rule.action_summary}</p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <p className="text-sm text-gray-600">{rule.condition_summary}</p>
                </td>
                <td className="px-4 py-3">
                  <span className={cn(
                    "inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full",
                    rule.status === "active"
                      ? "bg-green-100 text-green-800"
                      : "bg-gray-100 text-gray-800"
                  )}>
                    {rule.status === "active" ? (
                      <Play className="h-3 w-3" />
                    ) : (
                      <Pause className="h-3 w-3" />
                    )}
                    {rule.status === "active" ? "Active" : "Paused"}
                  </span>
                </td>
                <td className="px-4 py-3">
                  {rule.last_triggered ? (
                    <div className="flex items-center gap-1.5">
                      <Clock className="h-3.5 w-3.5 text-gray-400" />
                      <span className="text-sm text-gray-500">
                        {new Date(rule.last_triggered).toLocaleDateString()}
                      </span>
                      <span className="text-xs text-gray-400">({rule.trigger_count}x)</span>
                    </div>
                  ) : (
                    <span className="text-sm text-gray-400">Never</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <button className="text-sm text-blue-600 hover:underline">
                    {rule.status === "active" ? "Pause" : "Activate"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {rules.length === 0 && (
          <div className="px-4 py-8 text-center text-gray-500">
            No automated rules configured
          </div>
        )}
      </div>
    </div>
  );
}
