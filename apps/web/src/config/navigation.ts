import type { LucideIcon } from "lucide-react";
import {
  BarChart3,
  LayoutDashboard,
  Lightbulb,
  Link2,
  Megaphone,
  MessageSquare,
  Palette,
  Play,
  Radio,
  Settings,
  ShoppingBag,
  Sprout,
  Users,
} from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  group: "Main" | "Modules" | "Insights";
  badge?: string | number;
  /** Routes not yet available in v2 stay visible for parity but are non-interactive */
  disabled?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Overview", icon: LayoutDashboard, group: "Main" },
  { href: "/connect/shop", label: "Connect", icon: Link2, group: "Main" },
  { href: "/shops", label: "Commerce", icon: ShoppingBag, group: "Modules" },
  {
    href: "/ads",
    label: "Advertising",
    icon: Megaphone,
    group: "Modules",
    disabled: true,
  },
  {
    href: "/content",
    label: "Content",
    icon: Play,
    group: "Modules",
    disabled: true,
  },
  {
    href: "/creatives",
    label: "Creative Hub",
    icon: Palette,
    group: "Modules",
    disabled: true,
  },
  {
    href: "/creators",
    label: "Creators",
    icon: Users,
    group: "Modules",
    disabled: true,
  },
  {
    href: "/live",
    label: "LIVE",
    icon: Radio,
    group: "Modules",
    disabled: true,
  },
  {
    href: "/messaging",
    label: "Messaging",
    icon: MessageSquare,
    group: "Modules",
    disabled: true,
  },
  {
    href: "/organic",
    label: "Organic",
    icon: Sprout,
    group: "Modules",
    disabled: true,
  },
  {
    href: "/intelligence",
    label: "Intelligence",
    icon: Lightbulb,
    group: "Insights",
    disabled: true,
  },
  {
    href: "/analytics",
    label: "Analytics",
    icon: BarChart3,
    group: "Insights",
    disabled: true,
  },
];

export const SETTINGS_ITEM: NavItem = {
  href: "/settings",
  label: "Settings",
  icon: Settings,
  group: "Main",
};

export const ALL_NAV_ITEMS = [...NAV_ITEMS, SETTINGS_ITEM];

export function isNavActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}
