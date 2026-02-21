"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Wand2,
  Type,
  MousePointerClick,
  AlertTriangle,
  Sparkles,
  RefreshCw,
  CheckCircle,
  Clock,
  XCircle,
  ArrowRight,
  TrendingUp,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";

const MOCK_SUGGESTIONS = [
  {
    id: "sug-1",
    original: "Buy our amazing skincare products today!",
    suggestions: [
      "Unlock your glow with clinically proven skincare",
      "Your skin deserves science-backed care",
      "Transform your routine in just 7 days",
    ],
  },
  {
    id: "sug-2",
    original: "Best deals on electronics",
    suggestions: [
      "Top-rated tech at prices you'll love",
      "Smart gadgets, smarter savings",
      "Upgrade your setup without breaking the bank",
    ],
  },
];

const CTA_OPTIONS = [
  { label: "Shop Now", score: 92 },
  { label: "Learn More", score: 78 },
  { label: "Sign Up", score: 85 },
  { label: "Get Started", score: 88 },
  { label: "Download", score: 71 },
  { label: "Book Now", score: 82 },
];

interface FatigueItem {
  id: string;
  adName: string;
  frequency: number;
  daysActive: number;
  ctrDrop: number;
  status: "fatigued" | "at_risk" | "healthy";
}

const MOCK_FATIGUE: FatigueItem[] = [
  { id: "f-1", adName: "Summer Collection V2", frequency: 6.8, daysActive: 45, ctrDrop: -42, status: "fatigued" },
  { id: "f-2", adName: "Flash Sale Banner", frequency: 5.2, daysActive: 30, ctrDrop: -28, status: "fatigued" },
  { id: "f-3", adName: "New Arrivals Carousel", frequency: 4.1, daysActive: 21, ctrDrop: -15, status: "at_risk" },
  { id: "f-4", adName: "Brand Story Video", frequency: 2.3, daysActive: 14, ctrDrop: -3, status: "healthy" },
];

interface SmartFixTask {
  id: string;
  adName: string;
  issue: string;
  recommendation: string;
  status: "pending" | "applied" | "rejected";
}

const MOCK_FIX_TASKS: SmartFixTask[] = [
  { id: "sf-1", adName: "Summer Collection V2", issue: "Creative fatigue detected", recommendation: "Replace with new variant", status: "pending" },
  { id: "sf-2", adName: "Flash Sale Banner", issue: "Low contrast CTA button", recommendation: "Increase button contrast", status: "pending" },
  { id: "sf-3", adName: "Product Demo #4", issue: "Text too small for mobile", recommendation: "Increase font size to 18px", status: "applied" },
  { id: "sf-4", adName: "Retargeting Ad A", issue: "Outdated pricing shown", recommendation: "Update price to current", status: "pending" },
];

export default function SymphonyPage() {
  const [textInput, setTextInput] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(true);

  return (
    <>
      <PageHeader
        title="Symphony AI"
        description="AI-powered creative generation, text recommendations, and optimization"
        actions={
          <Link
            href="/creative-hub/generate"
            className="inline-flex items-center gap-1.5 rounded-lg border border-coral text-coral px-3 py-2 text-sm font-medium hover:bg-coral/5 transition-colors"
          >
            Open in Creative Hub
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        }
      />
      <PageShell
        header={
          <MetricBar>
            <MetricCard label="Smart Creatives" value={47} icon={Wand2} iconColor="text-purple" trend={{ value: 15, direction: "up", label: "this month" }} />
            <MetricCard label="Text Suggestions" value={156} icon={Type} iconColor="text-success" />
            <MetricCard label="Smart Fix Tasks" value={8} icon={RefreshCw} iconColor="text-info" />
            <MetricCard label="Fatigued Ads" value={3} icon={AlertTriangle} iconColor="text-coral" trend={{ value: 1, direction: "down", label: "vs last week" }} />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="AI Performance"
              description="AI-generated creatives are performing 23% better than manual creatives on average."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-danger" />}
              title="Fatigued Creatives"
              description="2 ads show severe fatigue with 40%+ CTR decline. Replace immediately."
              variant="danger"
              action={{ label: "View fatigued ads", onClick: () => {} }}
            />
          </InsightPanel>
        }
      >
        {/* Smart Creative Generator */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">Smart Creative Generator</h2>
          <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-[var(--shadow-card)]">
            <div className="flex gap-3 mb-4">
              <input
                type="text"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Describe your product or campaign goal..."
                className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
              />
              <button className="flex items-center gap-1.5 rounded-lg bg-purple px-4 py-2 text-sm font-medium text-white hover:bg-purple/90 transition-colors">
                <Sparkles className="h-4 w-4" />
                Generate
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {["Video Ad", "Carousel", "Static Image"].map((type) => (
                <div key={type} className="rounded-lg border border-dashed border-gray-200 p-4 text-center hover:border-purple/50 hover:bg-purple/5 transition-colors cursor-pointer">
                  <Wand2 className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-600">{type}</p>
                  <p className="text-xs text-gray-400 mt-1">AI-generated creative</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Smart Text Recommender */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">Smart Text Recommender</h2>
          <div className="space-y-4">
            {showSuggestions && MOCK_SUGGESTIONS.map((item) => (
              <div key={item.id} className="rounded-xl border border-gray-100 bg-white p-5 shadow-[var(--shadow-card)]">
                <p className="text-sm text-gray-500 mb-3">
                  <span className="font-medium text-gray-700">Original:</span> {item.original}
                </p>
                <div className="space-y-2">
                  {item.suggestions.map((sug, i) => (
                    <div key={i} className="flex items-center justify-between px-3 py-2 bg-success/5 rounded-lg border border-success/10">
                      <div className="flex items-center gap-2">
                        <Sparkles className="h-3.5 w-3.5 text-success" />
                        <span className="text-sm text-gray-900">{sug}</span>
                      </div>
                      <button className="text-xs text-success font-medium hover:underline">Apply</button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Optimizer */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">CTA Optimizer</h2>
          <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-[var(--shadow-card)]">
            <p className="text-xs text-gray-500 mb-4">AI-predicted performance scores for call-to-action buttons</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {CTA_OPTIONS.map((cta) => (
                <div key={cta.label} className="rounded-lg border border-gray-100 p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <MousePointerClick className="h-4 w-4 text-info" />
                    <span className={cn("text-xs font-semibold tabular-nums", cta.score >= 85 ? "text-success" : cta.score >= 75 ? "text-warning" : "text-gray-500")}>{cta.score}%</span>
                  </div>
                  <p className="text-sm font-medium text-gray-900">{cta.label}</p>
                  <div className="mt-2 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div className={cn("h-full rounded-full", cta.score >= 85 ? "bg-success" : cta.score >= 75 ? "bg-warning" : "bg-gray-400")} style={{ width: `${cta.score}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Creative Health */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-gray-900 mb-4">Creative Health</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Fatigue Monitor */}
            <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-[var(--shadow-card)]">
              <h3 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-coral" />
                Fatigue Monitor
              </h3>
              <div className="space-y-3">
                {MOCK_FATIGUE.map((item) => (
                  <div key={item.id} className="flex items-center justify-between px-3 py-2.5 rounded-lg bg-gray-50">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{item.adName}</p>
                      <p className="text-xs text-gray-500">Freq: {item.frequency} | {item.daysActive}d active</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={cn("text-xs font-medium tabular-nums", item.ctrDrop <= -20 ? "text-danger" : item.ctrDrop <= -10 ? "text-warning" : "text-success")}>{item.ctrDrop}% CTR</span>
                      <StatusBadge variant={item.status === "fatigued" ? "error" : item.status === "at_risk" ? "warning" : "active"} label={item.status === "fatigued" ? "Fatigued" : item.status === "at_risk" ? "At Risk" : "Healthy"} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Smart Fix Tasks */}
            <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-[var(--shadow-card)]">
              <h3 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                <RefreshCw className="h-4 w-4 text-info" />
                Smart Fix Tasks
              </h3>
              <div className="space-y-3">
                {MOCK_FIX_TASKS.map((task) => (
                  <div key={task.id} className="px-3 py-2.5 rounded-lg bg-gray-50">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-medium text-gray-900">{task.adName}</p>
                      <StatusBadge
                        variant={task.status === "applied" ? "active" : task.status === "rejected" ? "error" : "syncing"}
                        label={task.status === "applied" ? "Applied" : task.status === "rejected" ? "Rejected" : "Pending"}
                      />
                    </div>
                    <p className="text-xs text-gray-500">{task.issue}</p>
                    <p className="text-xs text-info mt-1">{task.recommendation}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </PageShell>
    </>
  );
}
