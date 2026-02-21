"use client";

import { useSyncExternalStore } from "react";

export type ToastVariant = "success" | "error" | "info" | "warning";

export interface ToastItem {
  id: string;
  variant: ToastVariant;
  message: string;
  duration?: number;
}

let toasts: ToastItem[] = [];
let listeners: Array<() => void> = [];

function emit() {
  listeners.forEach((l) => l());
}

export function addToast(variant: ToastVariant, message: string, duration = 4000) {
  const id = crypto.randomUUID();
  toasts = [...toasts, { id, variant, message, duration }];
  emit();
  if (duration > 0) {
    setTimeout(() => removeToast(id), duration);
  }
}

export function removeToast(id: string) {
  toasts = toasts.filter((t) => t.id !== id);
  emit();
}

export function useToasts(): ToastItem[] {
  return useSyncExternalStore(
    (cb) => {
      listeners.push(cb);
      return () => {
        listeners = listeners.filter((l) => l !== cb);
      };
    },
    () => toasts,
    () => []
  );
}

// Convenience helpers
export const toast = {
  success: (msg: string) => addToast("success", msg),
  error: (msg: string) => addToast("error", msg),
  info: (msg: string) => addToast("info", msg),
  warning: (msg: string) => addToast("warning", msg),
};
