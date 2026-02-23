"use client";

import { cn } from "@/lib/utils";

export interface PlatformTab {
  key: string;
  label: string;
}

interface PlatformTabsProps {
  tabs: PlatformTab[];
  value: string;
  onChange: (key: string) => void;
  className?: string;
}

export function PlatformTabs({ tabs, value, onChange, className }: PlatformTabsProps) {
  return (
    <div className={cn("flex items-center gap-1 rounded-lg bg-gray-100 p-1 mb-4", className)}>
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={cn(
            "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
            value === tab.key
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-500 hover:text-gray-700"
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
