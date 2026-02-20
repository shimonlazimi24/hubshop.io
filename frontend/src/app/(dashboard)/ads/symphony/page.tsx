"use client";

import { useState } from "react";
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
} from "lucide-react";
import { cn } from "@/lib/utils";

const KPI_CARDS = [
  {
    label: "Smart Creatives",
    value: 47,
    icon: Wand2,
    color: "text-purple bg-purple/5 border-purple/10",
    iconColor: "text-purple",
  },
  {
    label: "Text Suggestions",
    value: 156,
    icon: Type,
    color: "text-emerald-600 bg-emerald-50 border-emerald-100",
    iconColor: "text-emerald-500",
  },
  {
    label: "Smart Fix Tasks",
    value: 8,
    icon: RefreshCw,
    color: "text-blue-600 bg-blue-50 border-blue-100",
    iconColor: "text-blue-500",
  },
  {
    label: "Fatigued Ads",
    value: 3,
    icon: AlertTriangle,
    color: "text-coral bg-coral/5 border-coral/10",
    iconColor: "text-coral",
  },
];

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
    <div className="max-w-6xl">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
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

      {/* Smart Creative Generator */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Smart Creative Generator
        </h2>
        <div className="rounded-xl border border-gray-100 bg-white p-5">
          <div className="flex gap-3 mb-4">
            <input
              type="text"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Describe your product or campaign goal..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <button className="flex items-center gap-1.5 rounded-lg bg-purple px-4 py-2 text-sm font-medium text-white hover:bg-purple/90 transition-colors">
              <Sparkles className="h-4 w-4" />
              Generate
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {["Video Ad", "Carousel", "Static Image"].map((type) => (
              <div
                key={type}
                className="rounded-lg border border-dashed border-gray-200 p-4 text-center hover:border-purple/50 hover:bg-purple/5 transition-colors cursor-pointer"
              >
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
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Smart Text Recommender
        </h2>
        <div className="space-y-4">
          {showSuggestions &&
            MOCK_SUGGESTIONS.map((item) => (
              <div
                key={item.id}
                className="rounded-xl border border-gray-100 bg-white p-5"
              >
                <p className="text-sm text-gray-500 mb-3">
                  <span className="font-medium text-gray-700">Original:</span>{" "}
                  {item.original}
                </p>
                <div className="space-y-2">
                  {item.suggestions.map((sug, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between px-3 py-2 bg-emerald-50 rounded-lg"
                    >
                      <div className="flex items-center gap-2">
                        <Sparkles className="h-3.5 w-3.5 text-emerald-500" />
                        <span className="text-sm text-gray-900">{sug}</span>
                      </div>
                      <button className="text-xs text-emerald-600 font-medium hover:underline">
                        Apply
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* CTA Optimizer */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          CTA Optimizer
        </h2>
        <div className="rounded-xl border border-gray-100 bg-white p-5">
          <p className="text-xs text-gray-500 mb-4">
            AI-predicted performance scores for call-to-action buttons
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {CTA_OPTIONS.map((cta) => (
              <div
                key={cta.label}
                className="rounded-lg border border-gray-100 p-4 hover:shadow-sm transition-shadow"
              >
                <div className="flex items-center justify-between mb-2">
                  <MousePointerClick className="h-4 w-4 text-blue-500" />
                  <span
                    className={cn(
                      "text-xs font-semibold",
                      cta.score >= 85
                        ? "text-green-600"
                        : cta.score >= 75
                        ? "text-yellow-600"
                        : "text-gray-500"
                    )}
                  >
                    {cta.score}%
                  </span>
                </div>
                <p className="text-sm font-medium text-gray-900">{cta.label}</p>
                <div className="mt-2 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={cn(
                      "h-full rounded-full",
                      cta.score >= 85
                        ? "bg-green-500"
                        : cta.score >= 75
                        ? "bg-yellow-500"
                        : "bg-gray-400"
                    )}
                    style={{ width: `${cta.score}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Creative Health — Fatigue + Fix */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 mb-4">
          Creative Health
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Fatigue Monitor */}
          <div className="rounded-xl border border-gray-100 bg-white p-5">
            <h3 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-coral" />
              Fatigue Monitor
            </h3>
            <div className="space-y-3">
              {MOCK_FATIGUE.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between px-3 py-2.5 rounded-lg bg-gray-50"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900">{item.adName}</p>
                    <p className="text-xs text-gray-500">
                      Freq: {item.frequency} | {item.daysActive}d active
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        "text-xs font-medium",
                        item.ctrDrop <= -20 ? "text-red-600" : item.ctrDrop <= -10 ? "text-yellow-600" : "text-green-600"
                      )}
                    >
                      {item.ctrDrop}% CTR
                    </span>
                    <span
                      className={cn(
                        "px-2 py-0.5 text-xs rounded-full",
                        item.status === "fatigued"
                          ? "bg-red-100 text-red-700"
                          : item.status === "at_risk"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-green-100 text-green-700"
                      )}
                    >
                      {item.status === "fatigued" ? "Fatigued" : item.status === "at_risk" ? "At Risk" : "Healthy"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Smart Fix Tasks */}
          <div className="rounded-xl border border-gray-100 bg-white p-5">
            <h3 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
              <RefreshCw className="h-4 w-4 text-blue-500" />
              Smart Fix Tasks
            </h3>
            <div className="space-y-3">
              {MOCK_FIX_TASKS.map((task) => (
                <div
                  key={task.id}
                  className="px-3 py-2.5 rounded-lg bg-gray-50"
                >
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-medium text-gray-900">{task.adName}</p>
                    <span
                      className={cn(
                        "inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full",
                        task.status === "applied"
                          ? "bg-green-100 text-green-700"
                          : task.status === "rejected"
                          ? "bg-red-100 text-red-700"
                          : "bg-blue-100 text-blue-700"
                      )}
                    >
                      {task.status === "applied" ? (
                        <CheckCircle className="h-3 w-3" />
                      ) : task.status === "rejected" ? (
                        <XCircle className="h-3 w-3" />
                      ) : (
                        <Clock className="h-3 w-3" />
                      )}
                      {task.status === "applied" ? "Applied" : task.status === "rejected" ? "Rejected" : "Pending"}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">{task.issue}</p>
                  <p className="text-xs text-blue-600 mt-1">{task.recommendation}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
