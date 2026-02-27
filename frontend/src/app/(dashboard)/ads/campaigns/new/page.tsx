"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Megaphone,
  Target,
  ShoppingCart,
  Eye,
  Download,
  Users,
  Video,
  Sparkles,
  ChevronRight,
  ChevronLeft,
  Check,
  DollarSign,
  Rocket,
  ArrowLeft,
} from "lucide-react";
import Link from "next/link";

import {
  createCampaign,
  listAdAccounts,
  type AdAccount,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { toast } from "@/lib/toast-store";
import { PageShell } from "@/components/ui/page-shell";
import { PageHeader } from "@/components/dashboard/page-header";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { cn } from "@/lib/utils";
import { useWorkspace } from "@/hooks/useWorkspace";


/* ───── Step Definitions ───── */
const STEPS = [
  { label: "Objective", icon: Target },
  { label: "Details", icon: Megaphone },
  { label: "Budget", icon: DollarSign },
  { label: "Review", icon: Rocket },
] as const;

/* ───── Objectives ───── */
const OBJECTIVES = [
  {
    value: "TRAFFIC",
    label: "Traffic",
    description: "Send people to your website or app",
    icon: Target,
    color: "text-coral",
  },
  {
    value: "CONVERSIONS",
    label: "Conversions",
    description: "Drive valuable actions like purchases or sign-ups",
    icon: ShoppingCart,
    color: "text-success",
  },
  {
    value: "APP_INSTALL",
    label: "App Install",
    description: "Get more people to install your app",
    icon: Download,
    color: "text-info",
  },
  {
    value: "REACH",
    label: "Reach",
    description: "Show your ad to the maximum number of people",
    icon: Users,
    color: "text-purple",
  },
  {
    value: "VIDEO_VIEWS",
    label: "Video Views",
    description: "Get more people to watch your video content",
    icon: Video,
    color: "text-cyan",
  },
  {
    value: "LEAD_GENERATION",
    label: "Lead Generation",
    description: "Collect leads with instant forms",
    icon: Sparkles,
    color: "text-warning",
  },
  {
    value: "PRODUCT_SALES",
    label: "Product Sales",
    description: "Sell products from your TikTok Shop catalog",
    icon: ShoppingCart,
    color: "text-coral",
  },
] as const;

/* ───── Budget Modes ───── */
const BUDGET_MODES = [
  {
    value: "BUDGET_MODE_DAY",
    label: "Daily Budget",
    description: "Set a maximum spend per day. Best for ongoing campaigns.",
  },
  {
    value: "BUDGET_MODE_TOTAL",
    label: "Lifetime Budget",
    description: "Set a total spend for the entire campaign duration.",
  },
  {
    value: "BUDGET_MODE_INFINITE",
    label: "No Limit",
    description: "No budget cap — campaign spends based on ad group budgets.",
  },
] as const;

export default function NewCampaignPage() {
  const { workspaceId: WORKSPACE_ID } = useWorkspace();
  const router = useRouter();
  const token = getAccessToken();
  const [step, setStep] = useState(0);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [adAccounts, setAdAccounts] = useState<AdAccount[]>([]);
  const [selectedAccount, setSelectedAccount] = useState("");
  const [objective, setObjective] = useState("");
  const [campaignName, setCampaignName] = useState("");
  const [budgetMode, setBudgetMode] = useState("BUDGET_MODE_DAY");
  const [budget, setBudget] = useState("");

  useEffect(() => {
    if (!token || !WORKSPACE_ID) return;
    listAdAccounts(WORKSPACE_ID, token)
      .then((accounts) => {
        setAdAccounts(accounts);
        if (accounts.length === 1) setSelectedAccount(accounts[0].id);
      })
      .catch(console.error);
  }, []);

  /* ───── Validation ───── */
  function canAdvance(): boolean {
    switch (step) {
      case 0:
        return !!objective;
      case 1:
        return !!campaignName.trim() && !!selectedAccount;
      case 2:
        return budgetMode === "BUDGET_MODE_INFINITE" || (!!budget && parseFloat(budget) > 0);
      case 3:
        return true;
      default:
        return false;
    }
  }

  /* ───── Submit ───── */
  async function handleLaunch() {
    if (!token || !WORKSPACE_ID || !selectedAccount) return;
    setSubmitting(true);
    try {
      await createCampaign(
        WORKSPACE_ID,
        {
          ad_account_id: selectedAccount,
          campaign_name: campaignName.trim(),
          objective_type: objective,
          budget_mode: budgetMode,
          budget: budgetMode !== "BUDGET_MODE_INFINITE" ? budget : undefined,
        },
        token
      );
      toast.success("Campaign created successfully!");
      router.push("/ads");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to create campaign";
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  }

  /* ───── Step Content ───── */
  function renderStep() {
    switch (step) {
      case 0:
        return (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-1">Choose your campaign objective</h2>
            <p className="text-sm text-gray-500 mb-6">What do you want to achieve with this campaign?</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {OBJECTIVES.map((obj) => {
                const Icon = obj.icon;
                const selected = objective === obj.value;
                return (
                  <button
                    key={obj.value}
                    onClick={() => setObjective(obj.value)}
                    className={cn(
                      "flex items-start gap-3 rounded-xl border-2 p-4 text-left transition-all",
                      selected
                        ? "border-coral bg-coral/5 shadow-[var(--shadow-card)]"
                        : "border-gray-100 hover:border-gray-200 hover:bg-gray-50"
                    )}
                  >
                    <div className={cn("flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-gray-50", obj.color)}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-gray-900">{obj.label}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{obj.description}</p>
                    </div>
                    {selected && (
                      <div className="ml-auto flex-shrink-0">
                        <div className="flex h-5 w-5 items-center justify-center rounded-full bg-coral text-white">
                          <Check className="h-3 w-3" />
                        </div>
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        );

      case 1:
        return (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-1">Campaign details</h2>
            <p className="text-sm text-gray-500 mb-6">Name your campaign and select the ad account.</p>
            <div className="space-y-5 max-w-lg">
              <div>
                <label htmlFor="campaign-name" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Campaign Name
                </label>
                <input
                  id="campaign-name"
                  type="text"
                  value={campaignName}
                  onChange={(e) => setCampaignName(e.target.value)}
                  placeholder="e.g. Summer Collection Launch"
                  className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
                />
              </div>

              <div>
                <label htmlFor="ad-account" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Ad Account
                </label>
                {adAccounts.length === 0 ? (
                  <p className="text-sm text-gray-500">
                    No ad accounts found.{" "}
                    <Link href="/connect" className="text-coral hover:text-coral-dark">
                      Connect one first
                    </Link>
                  </p>
                ) : (
                  <select
                    id="ad-account"
                    value={selectedAccount}
                    onChange={(e) => setSelectedAccount(e.target.value)}
                    className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
                  >
                    <option value="">Select an account</option>
                    {adAccounts.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.advertiser_name}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-1">Set your budget</h2>
            <p className="text-sm text-gray-500 mb-6">Control how much you spend on this campaign.</p>
            <div className="space-y-4 max-w-lg">
              {/* Budget mode selection */}
              <div className="space-y-2">
                {BUDGET_MODES.map((mode) => {
                  const selected = budgetMode === mode.value;
                  return (
                    <button
                      key={mode.value}
                      onClick={() => setBudgetMode(mode.value)}
                      className={cn(
                        "w-full flex items-start gap-3 rounded-xl border-2 p-4 text-left transition-all",
                        selected
                          ? "border-coral bg-coral/5"
                          : "border-gray-100 hover:border-gray-200"
                      )}
                    >
                      <div className={cn(
                        "mt-0.5 flex h-5 w-5 items-center justify-center rounded-full border-2 flex-shrink-0",
                        selected ? "border-coral bg-coral" : "border-gray-300"
                      )}>
                        {selected && <Check className="h-3 w-3 text-white" />}
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-900">{mode.label}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{mode.description}</p>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Budget amount input */}
              {budgetMode !== "BUDGET_MODE_INFINITE" && (
                <div>
                  <label htmlFor="budget" className="block text-sm font-medium text-gray-700 mb-1.5">
                    {budgetMode === "BUDGET_MODE_DAY" ? "Daily Budget" : "Total Budget"} (USD)
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">$</span>
                    <input
                      id="budget"
                      type="number"
                      min="1"
                      step="0.01"
                      value={budget}
                      onChange={(e) => setBudget(e.target.value)}
                      placeholder={budgetMode === "BUDGET_MODE_DAY" ? "50.00" : "500.00"}
                      className="w-full rounded-lg border border-gray-200 pl-7 pr-4 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
                    />
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    {budgetMode === "BUDGET_MODE_DAY"
                      ? "TikTok recommends at least $20/day for optimal delivery."
                      : "TikTok recommends at least $50 lifetime budget."}
                  </p>
                </div>
              )}
            </div>
          </div>
        );

      case 3:
        return (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-1">Review and launch</h2>
            <p className="text-sm text-gray-500 mb-6">Confirm your campaign settings before creating.</p>

            <div className="max-w-lg space-y-4">
              <ReviewRow
                label="Objective"
                value={OBJECTIVES.find((o) => o.value === objective)?.label ?? objective}
                onEdit={() => setStep(0)}
              />
              <ReviewRow
                label="Campaign Name"
                value={campaignName}
                onEdit={() => setStep(1)}
              />
              <ReviewRow
                label="Ad Account"
                value={adAccounts.find((a) => a.id === selectedAccount)?.advertiser_name ?? selectedAccount}
                onEdit={() => setStep(1)}
              />
              <ReviewRow
                label="Budget Mode"
                value={BUDGET_MODES.find((m) => m.value === budgetMode)?.label ?? budgetMode}
                onEdit={() => setStep(2)}
              />
              {budgetMode !== "BUDGET_MODE_INFINITE" && (
                <ReviewRow
                  label={budgetMode === "BUDGET_MODE_DAY" ? "Daily Budget" : "Total Budget"}
                  value={`$${parseFloat(budget || "0").toFixed(2)}`}
                  onEdit={() => setStep(2)}
                />
              )}

              <div className="rounded-lg border border-info/20 bg-info/5 p-4 mt-6">
                <p className="text-sm text-gray-700">
                  Your campaign will be created in <strong>draft</strong> status. After creation, add ad groups and creatives, then enable the campaign to start delivery.
                </p>
              </div>
            </div>
          </div>
        );
    }
  }

  return (
    <>
      <PageHeader
        title="Create Campaign"
        description="Launch a new TikTok ad campaign"
        actions={
          <Link
            href="/ads"
            className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Campaigns
          </Link>
        }
      />

      <PageShell
        aside={
          <InsightPanel>
            <InsightItem
              icon={<Target className="h-4 w-4 text-coral" />}
              title="Choose the right objective"
              description="Your objective determines how TikTok optimizes ad delivery. Conversions and Product Sales typically deliver the best ROAS."
            />
            <InsightItem
              icon={<DollarSign className="h-4 w-4 text-success" />}
              title="Budget tips"
              description="Start with at least $20/day. TikTok needs 50+ conversions per week to optimize effectively."
              variant="success"
            />
            <InsightItem
              icon={<Sparkles className="h-4 w-4 text-purple" />}
              title="What's next after creation?"
              description="After creating the campaign, add ad groups with targeting, then attach creatives. Enable when ready to launch."
            />
          </InsightPanel>
        }
      >
        {/* ─── Stepper ─── */}
        <div className="mb-8">
          <div className="flex items-center gap-2">
            {STEPS.map((s, i) => {
              const Icon = s.icon;
              const isActive = i === step;
              const isDone = i < step;
              return (
                <div key={s.label} className="flex items-center gap-2">
                  <button
                    onClick={() => i < step && setStep(i)}
                    disabled={i > step}
                    className={cn(
                      "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all",
                      isActive && "bg-coral text-white shadow-[var(--shadow-card)]",
                      isDone && "bg-success/10 text-success cursor-pointer hover:bg-success/20",
                      !isActive && !isDone && "text-gray-400 cursor-not-allowed"
                    )}
                  >
                    {isDone ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <Icon className="h-4 w-4" />
                    )}
                    <span className="hidden sm:inline">{s.label}</span>
                  </button>
                  {i < STEPS.length - 1 && (
                    <ChevronRight className="h-4 w-4 text-gray-300 flex-shrink-0" />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* ─── Step Content ─── */}
        <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-[var(--shadow-card)] mb-6">
          {renderStep()}
        </div>

        {/* ─── Navigation ─── */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setStep(Math.max(0, step - 1))}
            disabled={step === 0}
            className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="h-4 w-4" />
            Back
          </button>

          {step < STEPS.length - 1 ? (
            <button
              onClick={() => setStep(step + 1)}
              disabled={!canAdvance()}
              className="inline-flex items-center gap-1.5 rounded-lg bg-coral px-5 py-2.5 text-sm font-medium text-white hover:bg-coral-dark disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Continue
              <ChevronRight className="h-4 w-4" />
            </button>
          ) : (
            <button
              onClick={handleLaunch}
              disabled={submitting || !canAdvance()}
              className="inline-flex items-center gap-1.5 rounded-lg bg-coral px-5 py-2.5 text-sm font-medium text-white hover:bg-coral-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? (
                <>
                  <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Rocket className="h-4 w-4" />
                  Create Campaign
                </>
              )}
            </button>
          )}
        </div>
      </PageShell>
    </>
  );
}

/* ───── Review Row ───── */
function ReviewRow({
  label,
  value,
  onEdit,
}: {
  label: string;
  value: string;
  onEdit: () => void;
}) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
      <div>
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</p>
        <p className="text-sm font-medium text-gray-900 mt-0.5">{value}</p>
      </div>
      <button
        onClick={onEdit}
        className="text-xs font-medium text-coral hover:text-coral-dark transition-colors"
      >
        Edit
      </button>
    </div>
  );
}
