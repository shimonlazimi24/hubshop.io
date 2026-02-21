"use client";

import { Wand2, Type, Wrench, Sparkles, Clock, CheckCircle } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { StatusBadge } from "@/components/ui/status-badge";

interface Generation {
  id: string;
  type: "creative" | "text" | "fix";
  prompt: string;
  status: "completed" | "processing" | "failed";
  createdAt: string;
}

const MOCK_GENERATIONS: Generation[] = [
  { id: "1", type: "creative", prompt: "Generate a 15s video ad for summer sale with upbeat music", status: "completed", createdAt: "2026-02-21 14:30" },
  { id: "2", type: "text", prompt: "Write 5 ad copy variations for fitness product targeting Gen Z", status: "completed", createdAt: "2026-02-21 13:15" },
  { id: "3", type: "fix", prompt: "Auto-fix low contrast text on 'Holiday Promo Banner'", status: "completed", createdAt: "2026-02-21 11:00" },
  { id: "4", type: "creative", prompt: "Create carousel ad for new product line launch", status: "processing", createdAt: "2026-02-21 10:45" },
  { id: "5", type: "text", prompt: "Generate CTA variations for retargeting campaign", status: "completed", createdAt: "2026-02-20 16:20" },
  { id: "6", type: "fix", prompt: "Optimize video resolution and aspect ratio for TikTok feed", status: "completed", createdAt: "2026-02-20 14:00" },
  { id: "7", type: "creative", prompt: "Generate UGC-style video for testimonial campaign", status: "failed", createdAt: "2026-02-20 09:30" },
  { id: "8", type: "text", prompt: "Write product description for catalog listing", status: "completed", createdAt: "2026-02-19 17:45" },
];

const TYPE_CONFIG: Record<string, { label: string; variant: "active" | "syncing" | "warning" }> = {
  creative: { label: "Creative", variant: "active" },
  text: { label: "Text", variant: "syncing" },
  fix: { label: "Fix", variant: "warning" },
};

const STATUS_VARIANT: Record<string, "active" | "syncing" | "error"> = {
  completed: "active",
  processing: "syncing",
  failed: "error",
};

const GENERATION_COLUMNS: Column<Generation>[] = [
  {
    key: "type",
    header: "Type",
    render: (row) => {
      const cfg = TYPE_CONFIG[row.type];
      return <StatusBadge variant={cfg.variant} label={cfg.label} />;
    },
  },
  {
    key: "prompt",
    header: "Prompt / Input",
    render: (row) => (
      <span className="text-gray-700 line-clamp-1 max-w-md">{row.prompt}</span>
    ),
  },
  {
    key: "status",
    header: "Status",
    render: (row) => (
      <StatusBadge
        variant={STATUS_VARIANT[row.status]}
        label={row.status.charAt(0).toUpperCase() + row.status.slice(1)}
      />
    ),
  },
  {
    key: "createdAt",
    header: "Created At",
    sortable: true,
    render: (row) => <span className="text-gray-500 tabular-nums">{row.createdAt}</span>,
  },
  {
    key: "actions",
    header: "",
    className: "w-20",
    render: (row) =>
      row.status === "completed" ? (
        <button className="text-xs font-medium text-coral hover:text-coral-dark transition-colors">
          View
        </button>
      ) : row.status === "processing" ? (
        <span className="text-xs text-gray-400">Processing...</span>
      ) : (
        <button className="text-xs font-medium text-gray-500 hover:text-gray-700 transition-colors">
          Retry
        </button>
      ),
  },
];

const WORKFLOWS = [
  {
    title: "Smart Creative",
    description: "Generate AI-powered creative assets from text prompts, reference images, or product catalogs.",
    icon: Wand2,
    gradient: "from-coral to-pink-500",
  },
  {
    title: "Smart Text",
    description: "Get AI text recommendations for ad copy, CTAs, captions, and product descriptions.",
    icon: Type,
    gradient: "from-purple-500 to-indigo-500",
  },
  {
    title: "Smart Fix",
    description: "Auto-detect and fix creative issues like low contrast, wrong aspect ratio, or poor quality.",
    icon: Wrench,
    gradient: "from-cyan-500 to-teal-500",
  },
];

export default function CreativeGeneratePage() {
  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Creatives Generated"
            value={47}
            icon={Wand2}
            trend={{ value: 32, direction: "up", label: "this month" }}
            sparklineData={[12, 18, 22, 28, 35, 41, 47]}
          />
          <MetricCard
            label="Text Suggestions"
            value={128}
            icon={Type}
            trend={{ value: 18, direction: "up", label: "this month" }}
            sparklineData={[45, 62, 78, 89, 102, 115, 128]}
          />
          <MetricCard
            label="Smart Fixes"
            value={23}
            icon={Wrench}
            trend={{ value: 9, direction: "up", label: "this month" }}
            sparklineData={[8, 10, 13, 15, 18, 20, 23]}
          />
          <MetricCard
            label="CTA Recommendations"
            value={64}
            icon={Sparkles}
            trend={{ value: 25, direction: "up", label: "this month" }}
            sparklineData={[20, 28, 35, 42, 50, 57, 64]}
          />
        </MetricBar>
      }
      aside={
        <InsightPanel defaultOpen>
          <InsightItem
            icon={<CheckCircle className="h-4 w-4 text-success" />}
            title="AI Confidence Scores"
            description="Smart Creative generations have 87% average confidence score. Text suggestions score 92% relevance."
            variant="success"
          />
          <InsightItem
            icon={<Sparkles className="h-4 w-4 text-info" />}
            title="Trending Creative Styles"
            description="UGC-style videos and bold text overlays are trending on TikTok this week. Use Smart Creative to generate matching assets."
            variant="default"
            action={{ label: "Generate trending", onClick: () => {} }}
          />
          <InsightItem
            icon={<Clock className="h-4 w-4 text-warning" />}
            title="Best Practices"
            description="Keep videos under 15s for best engagement. Use clear CTAs in the first 3 seconds. Smart Text can help optimize."
            variant="warning"
          />
        </InsightPanel>
      }
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {WORKFLOWS.map((wf) => {
          const Icon = wf.icon;
          return (
            <button
              key={wf.title}
              className="group relative overflow-hidden rounded-xl p-6 text-left text-white shadow-[var(--shadow-card)] transition-all duration-[var(--duration-normal)] hover:shadow-[var(--shadow-panel)] hover:scale-[1.02]"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${wf.gradient}`} />
              <div className="relative">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/20 mb-4">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-bold mb-1">{wf.title}</h3>
                <p className="text-sm text-white/80 leading-relaxed">{wf.description}</p>
              </div>
            </button>
          );
        })}
      </div>

      <h3 className="text-sm font-semibold text-gray-900 mb-3">Recent Generations</h3>
      <DataTable
        columns={GENERATION_COLUMNS}
        data={MOCK_GENERATIONS}
        keyExtractor={(row) => row.id}
        emptyTitle="No generations yet"
        emptyDescription="Use the workflows above to generate your first AI-powered creative."
      />
    </PageShell>
  );
}
