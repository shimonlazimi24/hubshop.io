"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createCreatorCampaign } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

export default function NewCreatorCampaignPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [budget, setBudget] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const token = getAccessToken();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token || !name) return;
    setSubmitting(true);
    setError("");
    try {
      await createCreatorCampaign(
        WORKSPACE_ID,
        {
          name,
          description: description || undefined,
          budget: budget || undefined,
          start_date: startDate || undefined,
          end_date: endDate || undefined,
        },
        token
      );
      toast.success("Campaign created successfully");
      router.push("/creators/campaigns");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to create campaign";
      setError(msg);
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <PageShell>
      <div className="max-w-2xl">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Create Creator Campaign</h3>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-100 shadow-[var(--shadow-card)] p-6 space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Campaign Name *</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., Summer 2026 Launch" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" required />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Campaign goals and details..." rows={3} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Budget ($)</label>
              <input type="text" value={budget} onChange={(e) => setBudget(e.target.value)} placeholder="5000.00" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
            </div>
            <div />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Start Date</label>
              <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">End Date</label>
              <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
            </div>
          </div>

          {error && (
            <div className="text-sm text-danger bg-danger/5 border border-danger/20 rounded-lg p-3">{error}</div>
          )}

          <div className="flex gap-3 pt-2">
            <button type="submit" disabled={submitting || !name} className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 disabled:opacity-50 transition-colors">
              {submitting ? "Creating..." : "Create Campaign"}
            </button>
            <button type="button" onClick={() => router.back()} className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </PageShell>
  );
}
