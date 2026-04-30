import { forwardRef, type ButtonHTMLAttributes } from "react";
import { Link, type LinkProps } from "react-router-dom";
import { cn } from "@/lib/utils";

type LegacyVariant = "default" | "gradient" | "outline" | "ghost" | "danger";
export type ButtonVariant =
  | LegacyVariant
  | "primary"
  | "secondary";

type ButtonSize = "default" | "sm" | "lg";

function normalizeVariant(v: ButtonVariant): LegacyVariant {
  if (v === "primary") return "gradient";
  if (v === "secondary") return "outline";
  return v;
}

const variantStyles: Record<LegacyVariant, string> = {
  default: "bg-foreground text-white hover:bg-foreground/90",
  gradient:
    "gradient-bg text-white hover:opacity-90 shadow-lg shadow-coral/25",
  outline:
    "border-2 border-border bg-transparent hover:bg-surface text-foreground",
  ghost: "bg-transparent hover:bg-surface text-foreground",
  danger:
    "bg-danger text-white hover:bg-danger/90 border border-danger/50 shadow-sm",
};

const sizeStyles: Record<ButtonSize, string> = {
  default: "h-11 px-6 text-sm",
  sm: "h-9 px-4 text-sm",
  lg: "h-14 px-8 text-base",
};

const baseClass =
  "inline-flex items-center justify-center gap-2 rounded-[14px] font-semibold transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:pointer-events-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-coral/40";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    const nv = normalizeVariant(variant);
    return (
      <button
        ref={ref}
        className={cn(
          baseClass,
          variantStyles[nv],
          sizeStyles[size],
          className,
        )}
        {...props}
      />
    );
  },
);

Button.displayName = "Button";

export type LinkButtonProps = Omit<LinkProps, "className"> &
  Pick<ButtonProps, "variant" | "size"> & { className?: string };

export function LinkButton({
  className,
  variant = "gradient",
  size = "default",
  ...props
}: LinkButtonProps) {
  const nv = normalizeVariant(variant);
  return (
    <Link
      className={cn(
        baseClass,
        variantStyles[nv],
        sizeStyles[size],
        className,
      )}
      {...props}
    />
  );
}
