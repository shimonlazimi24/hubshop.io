import {
  LayoutDashboard,
  Link2,
  ShoppingBag,
  Megaphone,
  Play,
  Users,
  BarChart3,
  Settings,
  Lightbulb,
  Radio,
  MessageSquare,
  Sprout,
  Palette,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  group: "Main" | "Modules" | "Insights";
  badge?: string | number;
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/overview", label: "Overview", icon: LayoutDashboard, group: "Main" },
  { href: "/connect", label: "Connect", icon: Link2, group: "Main" },
  { href: "/commerce", label: "Commerce", icon: ShoppingBag, group: "Modules" },
  { href: "/ads", label: "Advertising", icon: Megaphone, group: "Modules" },
  { href: "/content", label: "Content", icon: Play, group: "Modules" },
  { href: "/creatives", label: "Creative Hub", icon: Palette, group: "Modules" },
  { href: "/creators", label: "Creators", icon: Users, group: "Modules" },
  { href: "/live", label: "LIVE", icon: Radio, group: "Modules" },
  { href: "/messaging", label: "Messaging", icon: MessageSquare, group: "Modules" },
  { href: "/organic", label: "Organic", icon: Sprout, group: "Modules" },
  { href: "/intelligence", label: "Intelligence", icon: Lightbulb, group: "Insights" },
  { href: "/analytics", label: "Analytics", icon: BarChart3, group: "Insights" },
];

export const SETTINGS_ITEM: NavItem = {
  href: "/settings",
  label: "Settings",
  icon: Settings,
  group: "Main",
};

export const ALL_NAV_ITEMS = [...NAV_ITEMS, SETTINGS_ITEM];
