"use client";

import { AnimatePresence, motion } from "framer-motion";
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useToasts, removeToast, type ToastVariant } from "@/lib/toast-store";

const ICON_MAP: Record<ToastVariant, typeof CheckCircle> = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
  warning: AlertTriangle,
};

const STYLE_MAP: Record<ToastVariant, string> = {
  success: "border-success/20 bg-success/5 text-success",
  error: "border-danger/20 bg-danger/5 text-danger",
  info: "border-info/20 bg-info/5 text-info",
  warning: "border-warning/20 bg-warning/5 text-warning",
};

export function ToastContainer() {
  const toasts = useToasts();

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm">
      <AnimatePresence>
        {toasts.map((t) => {
          const Icon = ICON_MAP[t.variant];
          return (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{ duration: 0.25 }}
              className={cn(
                "flex items-start gap-3 rounded-lg border border-border bg-background px-4 py-3 shadow-[var(--shadow-panel)]"
              )}
            >
              <Icon className={cn("h-5 w-5 mt-0.5 flex-shrink-0", STYLE_MAP[t.variant])} />
              <p className="text-sm text-foreground flex-1">{t.message}</p>
              <button
                onClick={() => removeToast(t.id)}
                className="text-foreground-secondary hover:text-foreground transition-colors flex-shrink-0"
              >
                <X className="h-4 w-4" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
