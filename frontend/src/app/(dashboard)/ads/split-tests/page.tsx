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
} from "lucide-react";
import { cn } from "@/lib/utils";

const KPI_CARDS = [
  {
    label: "Active Tests",
    value: 4,
    icon: FlaskConical,
    color: "text-purple bg-purple/5 border-purple/10",
    iconColor: "text-purple",
  },
  {
    label: "Completed Tests",
    value: 12,
    icon: CheckCircle2,
    color: "text-emerald-600 bg-emerald-50 border-emerald-100",
    iconColor: "text-emerald-500",
  },
  {
    label: "Avg Improvement",
    value: "+18.3%",
    icon: TrendingUp,
    color: "text-blue-600 bg-blue-50 border-blue-100",
    iconColor: "text-blue-500",
  },
];

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
  {
    id: "st-1",
    name: "CTA Button Color Test",
    type: "creative",
    status: "running",
    variants: 3,
    impressions: 245_000,
    winner: null,
    improvement: null,
    startDate: "2026-02-15",
    endDate: null,
  },
  {
    id: "st-2",
    name: "Headline Copy Variants",
    type: "creative",
    status: "running",
    variants: 4,
    impressions: 180_000,
    winner: null,
    improvement: null,
    startDate: "2026-02-17",
    endDate: null,
  },
  {
    id: "st-3",
    name: "Age Group Targeting",
    type: "audience",
    status: "running",
    variants: 2,
    impressions: 320_000,
    winner: null,
    improvement: null,
    startDate: "2026-02-12",
    endDate: null,
  },
  {
    id: "st-4",
    name: "Budget Pacing Strategy",
    type: "budget",
    status: "running",
    variants: 2,
    impressions: 150_000,
    winner: null,
    improvement: null,
    startDate: "2026-02-18",
    endDate: null,
  },
  {
    id: "st-5",
    name: "Video vs Carousel",
    type: "creative",
    status: "completed",
    variants: 2,
    impressions: 890_000,
    winner: "Variant A (Video)",
    improvement: 24.5,
    startDate: "2026-01-20",
    endDate: "2026-02-10",
  },
  {
    id: "st-6",
    name: "In-Feed vs TopView",
    type: "placement",
    status: "completed",
    variants: 2,
    impressions: 1_200_000,
    winner: "Variant B (TopView)",
    improvement: 31.2,
    startDate: "2026-01-15",
    endDate: "2026-02-05",
  },
  {
    id: "st-7",
    name: "Interest vs Lookalike",
    type: "audience",
    status: "completed",
    variants: 2,
    impressions: 560_000,
    winner: "Variant B (Lookalike)",
    improvement: 12.8,
    startDate: "2026-01-25",
    endDate: "2026-02-08",
  },
];

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return String(n);
}

const TYPE_COLORS: Record<string, string> = {
  creative: "bg-purple-100 text-purple-700",
  audience: "bg-blue-100 text-blue-700",
  placement: "bg-emerald-100 text-emerald-700",
  budget: "bg-yellow-100 text-yellow-700",
};

export default function SplitTestsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newType, setNewType] = useState("creative");
  const [selectedTest, setSelectedTest] = useState<SplitTest | null>(null);

  const activeTests = MOCK_TESTS.filter((t) => t.status === "running");
  const completedTests = MOCK_TESTS.filter((t) => t.status === "completed");

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
                {card.value}
              </p>
              <p className="text-xs text-gray-400 mt-1">{card.label}</p>
            </div>
          );
        })}
      </div>

      {/* Create New Test */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-gray-900">Active Split Tests</h2>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
        >
          {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showCreate ? "Cancel" : "New Test"}
        </button>
      </div>

      {showCreate && (
        <div className="rounded-xl border border-gray-100 bg-white p-5 mb-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Create Split Test</h3>
          <div className="space-y-3">
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Test name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <select
              value={newType}
              onChange={(e) => setNewType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="creative">Creative</option>
              <option value="audience">Audience</option>
              <option value="placement">Placement</option>
              <option value="budget">Budget</option>
            </select>
            <button
              disabled={!newName.trim()}
              className="px-4 py-2 bg-gray-900 text-white rounded-md text-sm font-medium hover:bg-gray-800 disabled:opacity-50"
            >
              Create Test
            </button>
          </div>
        </div>
      )}

      {/* Active Tests */}
      <div className="space-y-3 mb-8">
        {activeTests.map((test) => (
          <div
            key={test.id}
            className="rounded-xl border border-gray-100 bg-white p-5 hover:shadow-sm transition-shadow cursor-pointer"
            onClick={() => setSelectedTest(test)}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-purple/5">
                  <Play className="h-[18px] w-[18px] text-purple" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-900">{test.name}</h3>
                  <p className="text-xs text-gray-500">
                    Started {test.startDate} | {test.variants} variants
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-600">{formatNumber(test.impressions)} impr.</span>
                <span className={cn("px-2 py-0.5 text-xs rounded-full", TYPE_COLORS[test.type])}>
                  {test.type}
                </span>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700">
                  <Clock className="h-3 w-3" />
                  Running
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Completed Tests */}
      <h2 className="text-sm font-semibold text-gray-900 mb-4">Completed Tests</h2>
      <div className="bg-white rounded-lg border border-gray-200">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Test</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Impressions</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Winner</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Improvement</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {completedTests.map((test) => (
              <tr
                key={test.id}
                className="hover:bg-gray-50 cursor-pointer"
                onClick={() => setSelectedTest(test)}
              >
                <td className="px-4 py-3">
                  <p className="text-sm font-medium text-gray-900">{test.name}</p>
                  <p className="text-xs text-gray-500">{test.startDate} - {test.endDate}</p>
                </td>
                <td className="px-4 py-3">
                  <span className={cn("px-2 py-0.5 text-xs rounded-full", TYPE_COLORS[test.type])}>
                    {test.type}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {formatNumber(test.impressions)}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <Trophy className="h-3.5 w-3.5 text-yellow-500" />
                    <span className="text-sm text-gray-900">{test.winner}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="text-sm font-medium text-green-600">
                    +{test.improvement}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Results Viewer */}
      {selectedTest && (
        <div className="mt-6 rounded-xl border border-gray-100 bg-white p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-900">
              Test Details: {selectedTest.name}
            </h3>
            <button
              onClick={() => setSelectedTest(null)}
              className="text-gray-400 hover:text-gray-600"
            >
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
              <p className="text-sm font-medium text-gray-900">{selectedTest.impressions.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Status</p>
              <p className={cn(
                "text-sm font-medium",
                selectedTest.status === "running" ? "text-blue-600" : "text-green-600"
              )}>
                {selectedTest.status === "running" ? "Running" : "Completed"}
              </p>
            </div>
          </div>
          {selectedTest.winner && (
            <div className="mt-4 p-3 bg-green-50 rounded-lg">
              <div className="flex items-center gap-2">
                <Trophy className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-green-800">
                  Winner: {selectedTest.winner} (+{selectedTest.improvement}% improvement)
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
