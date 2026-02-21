"use client";

import { useState } from "react";
import {
  Fingerprint,
  UserCircle,
  Palette,
  Plus,
  X,
  ExternalLink,
  Image,
  TrendingUp,
  AlertTriangle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { FilterBar, FilterDropdown } from "@/components/ui/filter-bar";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { PageHeader } from "@/components/dashboard/page-header";

interface Identity {
  id: string;
  displayName: string;
  type: "tiktok_account" | "custom";
  profileImage: string | null;
  postsCount: number;
  adAccountId: string;
  createdAt: string;
}

const MOCK_IDENTITIES: Identity[] = [
  { id: "id-1", displayName: "@brandofficial", type: "tiktok_account", profileImage: null, postsCount: 245, adAccountId: "acc-001", createdAt: "2025-11-15" },
  { id: "id-2", displayName: "@brand_us", type: "tiktok_account", profileImage: null, postsCount: 128, adAccountId: "acc-001", createdAt: "2025-12-01" },
  { id: "id-3", displayName: "@brand_europe", type: "tiktok_account", profileImage: null, postsCount: 87, adAccountId: "acc-002", createdAt: "2026-01-05" },
  { id: "id-4", displayName: "@creator_collab", type: "tiktok_account", profileImage: null, postsCount: 34, adAccountId: "acc-001", createdAt: "2026-01-20" },
  { id: "id-5", displayName: "@brand_seasonal", type: "tiktok_account", profileImage: null, postsCount: 12, adAccountId: "acc-003", createdAt: "2026-02-01" },
  { id: "id-6", displayName: "Summer Promo Identity", type: "custom", profileImage: null, postsCount: 56, adAccountId: "acc-001", createdAt: "2026-01-10" },
  { id: "id-7", displayName: "Holiday Campaign", type: "custom", profileImage: null, postsCount: 42, adAccountId: "acc-001", createdAt: "2025-11-20" },
  { id: "id-8", displayName: "Product Launch Brand", type: "custom", profileImage: null, postsCount: 28, adAccountId: "acc-002", createdAt: "2026-01-25" },
  { id: "id-9", displayName: "Influencer Spark", type: "custom", profileImage: null, postsCount: 19, adAccountId: "acc-001", createdAt: "2026-02-05" },
  { id: "id-10", displayName: "Gen Z Voice", type: "custom", profileImage: null, postsCount: 15, adAccountId: "acc-003", createdAt: "2026-02-10" },
  { id: "id-11", displayName: "B2B Enterprise", type: "custom", profileImage: null, postsCount: 8, adAccountId: "acc-002", createdAt: "2026-02-14" },
  { id: "id-12", displayName: "Local Store Voice", type: "custom", profileImage: null, postsCount: 3, adAccountId: "acc-003", createdAt: "2026-02-18" },
];

export default function IdentitiesPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newType, setNewType] = useState<"tiktok_account" | "custom">("custom");
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");

  const filtered = MOCK_IDENTITIES.filter((i) => {
    if (typeFilter && i.type !== typeFilter) return false;
    if (search && !i.displayName.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <>
      <PageHeader
        title="Identities"
        description="TikTok accounts and custom identities for your ad campaigns"
        actions={
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
          >
            {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            {showCreate ? "Cancel" : "Create Identity"}
          </button>
        }
      />
      <PageShell
        header={
          <MetricBar>
            <MetricCard label="Total Identities" value={12} icon={Fingerprint} iconColor="text-purple" />
            <MetricCard label="TikTok Accounts" value={5} icon={UserCircle} iconColor="text-success" />
            <MetricCard label="Custom Identities" value={7} icon={Palette} iconColor="text-info" />
          </MetricBar>
        }
        aside={
          <InsightPanel>
            <InsightItem
              icon={<TrendingUp className="h-4 w-4 text-success" />}
              title="Most Used"
              description="'@brandofficial' is used in 245 posts, your most active identity."
              variant="success"
            />
            <InsightItem
              icon={<AlertTriangle className="h-4 w-4 text-warning" />}
              title="Inactive Identities"
              description="3 custom identities have fewer than 10 posts. Consider consolidating."
              variant="warning"
            />
          </InsightPanel>
        }
      >
        <FilterBar
          searchValue={search}
          onSearchChange={setSearch}
          searchPlaceholder="Search identities..."
        >
          <FilterDropdown
            label="All Types"
            value={typeFilter}
            options={[
              { label: "TikTok Accounts", value: "tiktok_account" },
              { label: "Custom", value: "custom" },
            ]}
            onChange={setTypeFilter}
          />
        </FilterBar>

        {showCreate && (
          <div className="rounded-xl border border-gray-100 bg-white p-5 mb-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">New Identity</h3>
            <div className="space-y-3">
              <input type="text" value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Display name (e.g., @mybrand or Campaign Voice)" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral" />
              <select value={newType} onChange={(e) => setNewType(e.target.value as "tiktok_account" | "custom")} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral">
                <option value="tiktok_account">TikTok Account</option>
                <option value="custom">Custom Identity</option>
              </select>
              <div className="rounded-lg border border-dashed border-gray-200 p-4 text-center">
                <Image className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-xs text-gray-500">Upload profile image (optional)</p>
              </div>
              <button disabled={!newName.trim()} className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 disabled:opacity-50 transition-colors">Create Identity</button>
            </div>
          </div>
        )}

        {/* Identity Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((identity) => (
            <div
              key={identity.id}
              className="rounded-xl border border-gray-100 bg-white p-5 hover:shadow-[var(--shadow-card)] transition-shadow"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className={cn("flex h-10 w-10 items-center justify-center rounded-full", identity.type === "tiktok_account" ? "bg-success/10" : "bg-info/10")}>
                  {identity.type === "tiktok_account" ? <UserCircle className="h-5 w-5 text-success" /> : <Palette className="h-5 w-5 text-info" />}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-gray-900 truncate">{identity.displayName}</h3>
                  <p className="text-xs text-gray-500">{identity.type === "tiktok_account" ? "TikTok Account" : "Custom Identity"}</p>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <ExternalLink className="h-3.5 w-3.5 text-gray-400" />
                  <span className="text-sm text-gray-600">{identity.postsCount} post{identity.postsCount !== 1 ? "s" : ""}</span>
                </div>
                <span className={cn("px-2 py-0.5 text-xs rounded-full font-medium", identity.type === "tiktok_account" ? "bg-success/10 text-success" : "bg-info/10 text-info")}>
                  {identity.type === "tiktok_account" ? "Account" : "Custom"}
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-2">Created {identity.createdAt}</p>
            </div>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <Fingerprint className="h-8 w-8 text-gray-300 mx-auto mb-2" />
            <p className="text-sm">No identities match your filters</p>
          </div>
        )}
      </PageShell>
    </>
  );
}
