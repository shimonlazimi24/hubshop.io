"use client";

import { useState } from "react";
import Link from "next/link";
import { Image, Plus, Folder, Clock, X, FileImage, ArrowRight, Palette, Film } from "lucide-react";
import { cn } from "@/lib/utils";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";

interface CreativePortfolio {
  id: string;
  name: string;
  description: string;
  asset_count: number;
  created_at: string;
  updated_at: string;
  status: "active" | "archived";
}

const MOCK_PORTFOLIOS: CreativePortfolio[] = [
  {
    id: "port-1",
    name: "Spring Collection 2026",
    description: "Creative assets for the spring product launch campaign.",
    asset_count: 24,
    created_at: "2026-02-10T10:00:00Z",
    updated_at: "2026-02-20T08:30:00Z",
    status: "active",
  },
  {
    id: "port-2",
    name: "Brand Awareness - Q1",
    description: "Top-of-funnel brand awareness creative suite.",
    asset_count: 18,
    created_at: "2026-01-15T14:00:00Z",
    updated_at: "2026-02-18T16:00:00Z",
    status: "active",
  },
  {
    id: "port-3",
    name: "UGC Templates",
    description: "User-generated content style templates for Spark Ads.",
    asset_count: 12,
    created_at: "2026-01-28T09:00:00Z",
    updated_at: "2026-02-15T11:00:00Z",
    status: "active",
  },
  {
    id: "port-4",
    name: "Holiday Promos",
    description: "Holiday season promotional creatives.",
    asset_count: 32,
    created_at: "2025-11-01T10:00:00Z",
    updated_at: "2025-12-31T23:59:00Z",
    status: "archived",
  },
  {
    id: "port-5",
    name: "Product Demos",
    description: "Short-form product demonstration videos and images.",
    asset_count: 8,
    created_at: "2026-02-05T13:00:00Z",
    updated_at: "2026-02-19T10:00:00Z",
    status: "active",
  },
  {
    id: "port-6",
    name: "Retargeting Assets",
    description: "Dynamic creative assets for retargeting campaigns.",
    asset_count: 15,
    created_at: "2026-01-20T11:00:00Z",
    updated_at: "2026-02-17T09:00:00Z",
    status: "active",
  },
];

export default function CreativePortfoliosPage() {
  const [portfolios] = useState<CreativePortfolio[]>(MOCK_PORTFOLIOS);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  function handleCreate() {
    if (!newName.trim()) return;
    setNewName("");
    setNewDescription("");
    setShowCreate(false);
  }

  const filtered = portfolios.filter((p) => {
    if (statusFilter === "active" && p.status !== "active") return false;
    if (statusFilter === "archived" && p.status !== "archived") return false;
    if (search && !p.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const activeCount = portfolios.filter((p) => p.status === "active").length;
  const totalAssets = portfolios.reduce((sum, p) => sum + p.asset_count, 0);

  return (
    <>
      <PageHeader
        title="Creative Portfolios"
        description="Organize and manage your ad creative assets"
        actions={
          <Link
            href="/creative-hub"
            className="inline-flex items-center gap-1.5 rounded-lg border border-coral text-coral px-3 py-2 text-sm font-medium hover:bg-coral/5 transition-colors"
          >
            View all in Creative Hub
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        }
      />
      <PageShell
        header={
          <MetricBar>
            <MetricCard
              label="Active Portfolios"
              value={activeCount}
              icon={Folder}
              iconColor="text-purple"
              trend={{ value: 2, direction: "up", label: "this month" }}
            />
            <MetricCard
              label="Total Assets"
              value={totalAssets}
              icon={Image}
              iconColor="text-coral"
              trend={{ value: 15, direction: "up", label: "vs last month" }}
            />
            <MetricCard
              label="Videos"
              value={68}
              icon={Film}
              iconColor="text-info"
            />
            <MetricCard
              label="Images"
              value={41}
              icon={Palette}
              iconColor="text-success"
            />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<Film className="h-4 w-4 text-success" />}
              title="Top Format"
              description="Video creatives outperform images by 2.3x in engagement rate across your campaigns."
              variant="success"
            />
            <InsightItem
              icon={<Clock className="h-4 w-4 text-warning" />}
              title="Stale Assets"
              description="4 creatives haven't been updated in 30+ days. Consider refreshing for better performance."
              variant="warning"
              action={{ label: "Review assets", onClick: () => {} }}
            />
          </InsightPanel>
        }
      >
        <FilterBar
          searchValue={search}
          onSearchChange={setSearch}
          searchPlaceholder="Search portfolios..."
          actions={
            <button
              onClick={() => setShowCreate(!showCreate)}
              className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
            >
              {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
              {showCreate ? "Cancel" : "Create Portfolio"}
            </button>
          }
        >
          <FilterDropdown
            label="All Statuses"
            value={statusFilter}
            options={[
              { label: "Active", value: "active" },
              { label: "Archived", value: "archived" },
            ]}
            onChange={setStatusFilter}
          />
        </FilterBar>

        {showCreate && (
          <div className="rounded-xl border border-gray-100 bg-white p-5 mb-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">New Creative Portfolio</h3>
            <div className="space-y-3">
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Portfolio name"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
              />
              <textarea
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                placeholder="Description (optional)"
                rows={2}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
              />
              <button
                onClick={handleCreate}
                disabled={!newName.trim()}
                className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 disabled:opacity-50 transition-colors"
              >
                Create
              </button>
            </div>
          </div>
        )}

        {/* Portfolios Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((portfolio) => (
            <Link
              key={portfolio.id}
              href={`/ads/creatives/${portfolio.id}`}
              className={cn(
                "group rounded-xl border bg-white p-5 transition-all duration-200",
                portfolio.status === "archived"
                  ? "border-gray-100 bg-gray-50 opacity-60"
                  : "border-gray-100 hover:shadow-[var(--shadow-panel)] hover:border-gray-200"
              )}
            >
              <div className="flex items-center gap-3 mb-3">
                <div className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-lg",
                  portfolio.status === "archived" ? "bg-gray-200" : "bg-purple/10"
                )}>
                  <Folder className={cn("h-5 w-5", portfolio.status === "archived" ? "text-gray-400" : "text-purple")} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900 truncate group-hover:text-gray-700 transition-colors">
                    {portfolio.name}
                  </p>
                </div>
              </div>
              <p className="text-xs text-gray-500 leading-relaxed mb-3 line-clamp-2">
                {portfolio.description}
              </p>
              <div className="flex items-center justify-between text-xs text-gray-400">
                <div className="flex items-center gap-1">
                  <FileImage className="h-3.5 w-3.5" />
                  <span>{portfolio.asset_count} assets</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  <span>{new Date(portfolio.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <Folder className="h-8 w-8 text-gray-300 mx-auto mb-2" />
            <p className="text-sm">No portfolios match your filters</p>
          </div>
        )}
      </PageShell>
    </>
  );
}
