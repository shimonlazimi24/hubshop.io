"use client";

import { useState } from "react";
import {
  FlaskConical,
  CheckCircle2,
  TrendingUp,
  Plus,
  X,
  Play,
  Clock,
  Trophy,
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

interface SplitTest {
  id: string;
  name: string;
  type: "creative" | "audience" | "placement" | "budget";
  status: "running" | "completed" | "draft";
  variants: number;
  impressions: number;
  winner: string | null;
  improvement: number | null;
  startDate: string;
  endDate: string | null;
}

const MOCK_TESTS: SplitTest[] = [
  { id: "st-1", name: "CTA Button Color Test", type: "creative", status: "running", variants: 3, impressions: 245_000, winner: null, improvement: null, startDate: "2026-02-15", endDate: null },
  { id: "st-2", name: "Headline Copy Variants", type: "creative", status: "running", variants: 4, impressions: 180_000, winner: null, improvement: null, startDate: "2026-02-17", endDate: null },
  { id: "st-3", name: "Age Group Targeting", type: "audience", status: "running", variants: 2, impressions: 320_000, winner: null, improvement: null, startDate: "2026-02-12", endDate: null },
  { id: "st-4", name: "Budget Pacing Strategy", type: "budget", status: "running", variants: 2, impressions: 150_000, winner: null, improvement: null, startDate: "2026-02-18", endDate: null },
  { id: "st-5", name: "Video vs Carousel", type: "creative", status: "completed", variants: 2, impressions: 890_000, winner: "Variant A (Video)", improvement: 24.5, startDate: "2026-01-20", endDate: "2026-02-10" },
  { id: "st-6", name: "In-Feed vs TopView", type: "placement", status: "completed", variants: 2, impressions: 1_200_000, winner: "Variant B (TopView)", improvement: 31.2, startDate: "2026-01-15", endDate: "2026-02-05" },
  { id: "st-7", name: "Interest vs Lookalike", type: "audience", status: "completed", variants: 2, impressions: 560_000, winner: "Variant B (Lookalike)", improvement: 12.8, startDate: "2026-01-25", endDate: "2026-02-08" },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return String(n);
}

export default function SplitTestsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newType, setNewType] = useState("creative");
  const [selectedTest, setSelectedTest] = useState<SplitTest | null>(null);

  const activeTests = MOCK_TESTS.filter((t) => t.status === "running");
  const completedTests = MOCK_TESTS.filter((t) => t.status === "completed");

  const completedColumns: Column<SplitTest>[] = [
    {
      key: "name",
      header: "Test",
      sortable: true,
      render: (row) => (
        <div>
          <p className="text-sm font-medium text-gray-900">{row.name}</p>
          <p className="text-xs text-gray-500">{row.startDate} - {row.endDate}</p>
        </div>
      ),
    },
    {
      key: "type",
      header: "Type",
      render: (row) => (
        <StatusBadge
          variant={row.type === "creative" ? "syncing" : row.type === "audience" ? "active" : row.type === "placement" ? "completed" : "warning"}
          label={row.type}
        />
      ),
    },
    {
      key: "impressions",
      header: "Impressions",
      sortable: true,
      render: (row) => <span className="text-sm text-gray-600 tabular-nums">{formatNumber(row.impressions)}</span>,
    },
    {
      key: "winner",
      header: "Winner",
      render: (row) => (
        <div className="flex items-center gap-1.5">
          <Trophy className="h-3.5 w-3.5 text-warning" />
          <span className="text-sm text-gray-900">{row.winner}</span>
        </div>
      ),
    },
    {
      key: "improvement",
      header: "Improvement",
      sortable: true,
      render: (row) => (
        <span className="text-sm font-medium text-success tabular-nums">+{row.improvement}%</span>
      ),
    },
  ];

  return (
    <>
      <PageHeader
        title="Split Tests"
        description="A/B testing for creatives, audiences, placements, and budgets"
        actions={
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
          >
            {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            {showCreate ? "Cancel" : "New Test"}
          </button>
        }
      />
      <PageShell
        header={
          <MetricBar>
            <MetricCard label="Active Tests" value={4} icon={FlaskConical} iconColor="text-purple" trend={{ value: 2, direction: "up", label: "this week" }} />
            <MetricCard label="Completed Tests" value={12} icon={CheckCircle2} iconColor="text-success" />
            <MetricCard label="Avg Improvement" value="+18.3%" icon={TrendingUp} iconColor="text-info" trend={{ value: 3.1, direction: "up", label: "vs last month" }} />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<Trophy className="h-4 w-4 text-success" />}
              title="Best Test Result"
              description="'In-Feed vs TopView' delivered +31.2% improvement. Apply TopView to more campaigns."
              variant="success"
              action={{ label: "Apply learnings", onClick: () => {} }}
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Test Duration"
              description="'CTA Button Color Test' needs 2 more days for statistical significance."
              variant="warning"
            />
          </InsightPanel>
        }
      >
        {showCreate && (
          <div className="rounded-xl border border-gray-100 bg-white p-5 mb-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Create Split Test</h3>
            <div className="space-y-3">
              <input type="text" value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Test name" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral" />
              <select value={newType} onChange={(e) => setNewType(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral">
                <option value="creative">Creative</option>
                <option value="audience">Audience</option>
                <option value="placement">Placement</option>
                <option value="budget">Budget</option>
              </select>
              <button disabled={!newName.trim()} className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 disabled:opacity-50 transition-colors">Create Test</button>
            </div>
          </div>
        )}

        {/* Active Tests */}
        <h2 className="text-sm font-semibold text-gray-900 mb-4">Active Split Tests</h2>
        <div className="space-y-3 mb-8">
          {activeTests.map((test) => (
            <div
              key={test.id}
              className="rounded-xl border border-gray-100 bg-white p-5 hover:shadow-[var(--shadow-card)] transition-shadow cursor-pointer"
              onClick={() => setSelectedTest(test)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-purple/5">
                    <Play className="h-[18px] w-[18px] text-purple" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900">{test.name}</h3>
                    <p className="text-xs text-gray-500">Started {test.startDate} | {test.variants} variants</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-600 tabular-nums">{formatNumber(test.impressions)} impr.</span>
                  <StatusBadge
                    variant={test.type === "creative" ? "syncing" : test.type === "audience" ? "active" : test.type === "placement" ? "completed" : "warning"}
                    label={test.type}
                  />
                  <StatusBadge variant="syncing" label="Running" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Completed Tests */}
        <h2 className="text-sm font-semibold text-gray-900 mb-4">Completed Tests</h2>
        <DataTable
          columns={completedColumns}
          data={completedTests}
          keyExtractor={(row) => row.id}
          onRowClick={(row) => setSelectedTest(row)}
          emptyTitle="No completed tests"
        />

        {/* Results Viewer */}
        {selectedTest && (
          <div className="mt-6 rounded-xl border border-gray-100 bg-white p-5 shadow-[var(--shadow-card)]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-900">Test Details: {selectedTest.name}</h3>
              <button onClick={() => setSelectedTest(null)} className="text-gray-400 hover:text-gray-600 transition-colors">
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-gray-500">Type</p>
                <p className="text-sm font-medium text-gray-900 capitalize">{selectedTest.type}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Variants</p>
                <p className="text-sm font-medium text-gray-900">{selectedTest.variants}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Impressions</p>
                <p className="text-sm font-medium text-gray-900 tabular-nums">{selectedTest.impressions.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Status</p>
                <StatusBadge variant={selectedTest.status === "running" ? "syncing" : "completed"} label={selectedTest.status === "running" ? "Running" : "Completed"} />
              </div>
            </div>
            {selectedTest.winner && (
              <div className="mt-4 p-3 bg-success/5 rounded-lg border border-success/10">
                <div className="flex items-center gap-2">
                  <Trophy className="h-4 w-4 text-success" />
                  <span className="text-sm font-medium text-success">
                    Winner: {selectedTest.winner} (+{selectedTest.improvement}% improvement)
                  </span>
                </div>
              </div>
            )}
          </div>
        )}
      </PageShell>
    </>
  );
}
