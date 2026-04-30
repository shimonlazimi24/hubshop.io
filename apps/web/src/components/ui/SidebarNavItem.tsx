import { NavLink } from "react-router-dom";
import type { LucideIcon } from "lucide-react";
import { cn } from "../../lib/cn";

export function SidebarNavItem({
  to,
  icon: Icon,
  label,
  end,
  badge,
  disabled,
  title,
}: {
  to: string;
  icon?: LucideIcon;
  label: string;
  end?: boolean;
  badge?: string;
  disabled?: boolean;
  title?: string;
}) {
  if (disabled) {
    return (
      <div
        title={title}
        className="flex cursor-not-allowed items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-500"
      >
        {Icon ? <Icon className="h-4 w-4 shrink-0 opacity-50" /> : null}
        <span className="flex-1">{label}</span>
        {badge ? (
          <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-medium uppercase text-slate-500">
            {badge}
          </span>
        ) : null}
      </div>
    );
  }

  return (
    <NavLink
      to={to}
      end={end}
      title={title}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
          isActive
            ? "bg-coral/15 text-white ring-1 ring-coral/40"
            : "text-slate-400 hover:bg-slate-800/80 hover:text-slate-100",
        )
      }
    >
      {Icon ? <Icon className="h-4 w-4 shrink-0 opacity-90" /> : null}
      <span className="flex-1">{label}</span>
      {badge ? (
        <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-medium uppercase text-slate-400">
          {badge}
        </span>
      ) : null}
    </NavLink>
  );
}

export function SidebarSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1">
      <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
        {title}
      </p>
      <div className="space-y-0.5">{children}</div>
    </div>
  );
}
