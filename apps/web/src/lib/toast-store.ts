import { useSyncExternalStore } from "react";

export type ToastVariant = "success" | "error" | "info" | "warning";

export interface ToastItem {
  id: string;
  variant: ToastVariant;
  message: string;
  duration?: number;
}

let toasts: ToastItem[] = [];
const listeners: Array<() => void> = [];

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
        const i = listeners.indexOf(cb);
        if (i >= 0) listeners.splice(i, 1);
      };
    },
    () => toasts,
    () => [],
  );
}
