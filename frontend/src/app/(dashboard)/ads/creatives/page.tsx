"use client";

import { useState } from "react";
import Link from "next/link";
import { Image, Plus, Folder, Clock, X, FileImage } from "lucide-react";
import { cn } from "@/lib/utils";

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

  function handleCreate() {
    if (!newName.trim()) return;
    // Placeholder: would call API to create portfolio
    setNewName("");
    setNewDescription("");
    setShowCreate(false);
  }

  const activePortfolios = portfolios.filter((p) => p.status === "active");
  const archivedPortfolios = portfolios.filter((p) => p.status === "archived");

  return (
    <div className="max-w-6xl">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">
          {activePortfolios.length} active portfolio{activePortfolios.length !== 1 ? "s" : ""}
        </p>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
        >
          {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showCreate ? "Cancel" : "Create Portfolio"}
        </button>
      </div>

      {showCreate && (
        <div className="rounded-xl border border-gray-100 bg-white p-5 mb-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">New Creative Portfolio</h3>
          <div className="space-y-3">
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Portfolio name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <textarea
              value={newDescription}
              onChange={(e) => setNewDescription(e.target.value)}
              placeholder="Description (optional)"
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <button
              onClick={handleCreate}
              disabled={!newName.trim()}
              className="px-4 py-2 bg-gray-900 text-white rounded-md text-sm font-medium hover:bg-gray-800 disabled:opacity-50"
            >
              Create
            </button>
          </div>
        </div>
      )}

      {/* Active Portfolios Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {activePortfolios.map((portfolio) => (
          <Link
            key={portfolio.id}
            href={`/ads/creatives/${portfolio.id}`}
            className="group rounded-xl border border-gray-100 bg-white p-5 hover:shadow-md hover:border-gray-200 transition-all duration-200"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple/10">
                <Folder className="h-5 w-5 text-purple" />
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

      {/* Archived */}
      {archivedPortfolios.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-3">Archived</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {archivedPortfolios.map((portfolio) => (
              <div
                key={portfolio.id}
                className="rounded-xl border border-gray-100 bg-gray-50 p-5 opacity-60"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-200">
                    <Folder className="h-5 w-5 text-gray-400" />
                  </div>
                  <p className="text-sm font-medium text-gray-600 truncate">{portfolio.name}</p>
                </div>
                <p className="text-xs text-gray-400 leading-relaxed mb-3 line-clamp-2">
                  {portfolio.description}
                </p>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>{portfolio.asset_count} assets</span>
                  <span>{new Date(portfolio.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
