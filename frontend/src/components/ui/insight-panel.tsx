"use client";

import { useState, type ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Lightbulb, ChevronRight, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface InsightPanelProps {
  children: ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

export function InsightPanel({ children, defaultOpen = false, className }: InsightPanelProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <>
      {/* Toggle button (visible when panel is closed) */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed right-0 top-1/2 -translate-y-1/2 z-40 flex items-center gap-1 rounded-l-lg border border-r-0 border-gray-200 bg-white px-2 py-3 shadow-[var(--shadow-card)] text-gray-500 hover:text-coral transition-colors"
        >
          <Lightbulb className="h-4 w-4" />
          <ChevronRight className="h-3 w-3 rotate-180" />
        </button>
      )}

      {/* Panel */}
      <AnimatePresence>
        {open && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 320, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className={cn(
              "hidden lg:block flex-shrink-0 border-l border-gray-100 bg-white overflow-hidden",
              className
            )}
          >
            <div className="w-[320px] h-full overflow-y-auto">
              <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
                <div className="flex items-center gap-2">
                  <Lightbulb className="h-4 w-4 text-coral" />
                  <h3 className="text-sm font-semibold text-gray-900">Insights</h3>
                </div>
                <button
                  onClick={() => setOpen(false)}
                  className="flex h-7 w-7 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
              <div className="p-5 space-y-4">
                {children}
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}

interface InsightItemProps {
  icon?: ReactNode;
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
  variant?: "default" | "success" | "warning" | "danger";
}

const VARIANT_BORDER: Record<string, string> = {
  default: "border-gray-100",
  success: "border-success/20",
  warning: "border-warning/20",
  danger: "border-danger/20",
};

export function InsightItem({ icon, title, description, action, variant = "default" }: InsightItemProps) {
  return (
    <div className={cn("rounded-lg border p-3", VARIANT_BORDER[variant])}>
      <div className="flex items-start gap-2.5">
        {icon && <span className="mt-0.5 flex-shrink-0">{icon}</span>}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900">{title}</p>
          <p className="text-xs text-gray-500 mt-0.5">{description}</p>
          {action && (
            <button
              onClick={action.onClick}
              className="text-xs font-medium text-coral hover:text-coral-dark mt-2 transition-colors"
            >
              {action.label} →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
