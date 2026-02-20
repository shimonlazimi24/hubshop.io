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
} from "lucide-react";
import { cn } from "@/lib/utils";

const KPI_CARDS = [
  {
    label: "Total Identities",
    value: 12,
    icon: Fingerprint,
    color: "text-purple bg-purple/5 border-purple/10",
    iconColor: "text-purple",
  },
  {
    label: "TikTok Accounts",
    value: 5,
    icon: UserCircle,
    color: "text-emerald-600 bg-emerald-50 border-emerald-100",
    iconColor: "text-emerald-500",
  },
  {
    label: "Custom Identities",
    value: 7,
    icon: Palette,
    color: "text-blue-600 bg-blue-50 border-blue-100",
    iconColor: "text-blue-500",
  },
];

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
  {
    id: "id-1",
    displayName: "@brandofficial",
    type: "tiktok_account",
    profileImage: null,
    postsCount: 245,
    adAccountId: "acc-001",
    createdAt: "2025-11-15",
  },
  {
    id: "id-2",
    displayName: "@brand_us",
    type: "tiktok_account",
    profileImage: null,
    postsCount: 128,
    adAccountId: "acc-001",
    createdAt: "2025-12-01",
  },
  {
    id: "id-3",
    displayName: "@brand_europe",
    type: "tiktok_account",
    profileImage: null,
    postsCount: 87,
    adAccountId: "acc-002",
    createdAt: "2026-01-05",
  },
  {
    id: "id-4",
    displayName: "@creator_collab",
    type: "tiktok_account",
    profileImage: null,
    postsCount: 34,
    adAccountId: "acc-001",
    createdAt: "2026-01-20",
  },
  {
    id: "id-5",
    displayName: "@brand_seasonal",
    type: "tiktok_account",
    profileImage: null,
    postsCount: 12,
    adAccountId: "acc-003",
    createdAt: "2026-02-01",
  },
  {
    id: "id-6",
    displayName: "Summer Promo Identity",
    type: "custom",
    profileImage: null,
    postsCount: 56,
    adAccountId: "acc-001",
    createdAt: "2026-01-10",
  },
  {
    id: "id-7",
    displayName: "Holiday Campaign",
    type: "custom",
    profileImage: null,
    postsCount: 42,
    adAccountId: "acc-001",
    createdAt: "2025-11-20",
  },
  {
    id: "id-8",
    displayName: "Product Launch Brand",
    type: "custom",
    profileImage: null,
    postsCount: 28,
    adAccountId: "acc-002",
    createdAt: "2026-01-25",
  },
  {
    id: "id-9",
    displayName: "Influencer Spark",
    type: "custom",
    profileImage: null,
    postsCount: 19,
    adAccountId: "acc-001",
    createdAt: "2026-02-05",
  },
  {
    id: "id-10",
    displayName: "Gen Z Voice",
    type: "custom",
    profileImage: null,
    postsCount: 15,
    adAccountId: "acc-003",
    createdAt: "2026-02-10",
  },
  {
    id: "id-11",
    displayName: "B2B Enterprise",
    type: "custom",
    profileImage: null,
    postsCount: 8,
    adAccountId: "acc-002",
    createdAt: "2026-02-14",
  },
  {
    id: "id-12",
    displayName: "Local Store Voice",
    type: "custom",
    profileImage: null,
    postsCount: 3,
    adAccountId: "acc-003",
    createdAt: "2026-02-18",
  },
];

export default function IdentitiesPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newType, setNewType] = useState<"tiktok_account" | "custom">("custom");
  const [filter, setFilter] = useState<"all" | "tiktok_account" | "custom">("all");

  const filtered = filter === "all"
    ? MOCK_IDENTITIES
    : MOCK_IDENTITIES.filter((i) => i.type === filter);

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

      {/* Filter + Create */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex gap-2">
          {(["all", "tiktok_account", "custom"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "px-3 py-1.5 text-sm rounded-md transition-colors",
                filter === f
                  ? "bg-gray-900 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              )}
            >
              {f === "all" ? "All" : f === "tiktok_account" ? "TikTok Accounts" : "Custom"}
            </button>
          ))}
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
        >
          {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showCreate ? "Cancel" : "Create Identity"}
        </button>
      </div>

      {/* Create Identity Form */}
      {showCreate && (
        <div className="rounded-xl border border-gray-100 bg-white p-5 mb-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">New Identity</h3>
          <div className="space-y-3">
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Display name (e.g., @mybrand or Campaign Voice)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <select
              value={newType}
              onChange={(e) => setNewType(e.target.value as "tiktok_account" | "custom")}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="tiktok_account">TikTok Account</option>
              <option value="custom">Custom Identity</option>
            </select>
            <div className="rounded-lg border border-dashed border-gray-200 p-4 text-center">
              <Image className="h-8 w-8 text-gray-300 mx-auto mb-2" />
              <p className="text-xs text-gray-500">Upload profile image (optional)</p>
            </div>
            <button
              disabled={!newName.trim()}
              className="px-4 py-2 bg-gray-900 text-white rounded-md text-sm font-medium hover:bg-gray-800 disabled:opacity-50"
            >
              Create Identity
            </button>
          </div>
        </div>
      )}

      {/* Identity List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((identity) => (
          <div
            key={identity.id}
            className="rounded-xl border border-gray-100 bg-white p-5 hover:shadow-sm transition-shadow"
          >
            <div className="flex items-center gap-3 mb-3">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-full",
                  identity.type === "tiktok_account"
                    ? "bg-emerald-50"
                    : "bg-blue-50"
                )}
              >
                {identity.type === "tiktok_account" ? (
                  <UserCircle className="h-5 w-5 text-emerald-500" />
                ) : (
                  <Palette className="h-5 w-5 text-blue-500" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-gray-900 truncate">
                  {identity.displayName}
                </h3>
                <p className="text-xs text-gray-500">
                  {identity.type === "tiktok_account" ? "TikTok Account" : "Custom Identity"}
                </p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <ExternalLink className="h-3.5 w-3.5 text-gray-400" />
                <span className="text-sm text-gray-600">
                  {identity.postsCount} post{identity.postsCount !== 1 ? "s" : ""}
                </span>
              </div>
              <span
                className={cn(
                  "px-2 py-0.5 text-xs rounded-full",
                  identity.type === "tiktok_account"
                    ? "bg-emerald-100 text-emerald-700"
                    : "bg-blue-100 text-blue-700"
                )}
              >
                {identity.type === "tiktok_account" ? "Account" : "Custom"}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-2">
              Created {identity.createdAt}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
