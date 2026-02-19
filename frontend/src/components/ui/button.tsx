import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type ButtonVariant = "default" | "gradient" | "outline" | "ghost";
type ButtonSize = "default" | "sm" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const variantStyles: Record<ButtonVariant, string> = {
  default:
    "bg-foreground text-white hover:bg-foreground/90",
  gradient:
    "gradient-bg text-white hover:opacity-90 shadow-lg shadow-coral/25",
  outline:
    "border-2 border-border bg-transparent hover:bg-surface text-foreground",
  ghost:
    "bg-transparent hover:bg-surface text-foreground",
};

const sizeStyles: Record<ButtonSize, string> = {
  default: "h-11 px-6 text-sm",
  sm: "h-9 px-4 text-sm",
  lg: "h-14 px-8 text-base",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    return (
      <button
        type="button"
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-[14px] font-semibold transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:pointer-events-none",
          variantStyles[variant],
          sizeStyles[size],
          className
        )}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";
