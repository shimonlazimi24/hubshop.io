"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare, Bot, Inbox } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { cn } from "@/lib/utils";

const TABS = [
  {
    href: "/messaging",
    label: "Overview",
    icon: Inbox,
    exact: ["/messaging"],
    prefix: [],
  },
  {
    href: "/messaging/auto-messages",
    label: "Auto-Messages",
    icon: Bot,
    exact: [],
    prefix: ["/messaging/auto-messages"],
  },
];

export default function MessagingLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // Hide tabs on conversation detail pages
  const isConversation = /^\/messaging\/[^/]+$/.test(pathname) && pathname !== "/messaging";
  const isAutoMessages = pathname.startsWith("/messaging/auto-messages");
  const showTabs = !isConversation || isAutoMessages;

  return (
    <div>
      <PageHeader
        title="Messaging"
        description="Manage conversations, auto-replies, and customer engagement."
      />

      {showTabs && (
        <div className="border-b border-gray-200 mb-6">
          <nav className="flex gap-1">
            {TABS.map((tab) => {
              const isActive =
                tab.exact.some((m) => pathname === m) ||
                tab.prefix.some(
                  (m) => pathname === m || pathname.startsWith(m + "/")
                );
              const Icon = tab.icon;
              return (
                <Link
                  key={tab.href}
                  href={tab.href}
                  className={cn(
                    "flex items-center gap-1.5 px-3 pb-2.5 text-sm font-medium border-b-2 transition-colors",
                    isActive
                      ? "border-coral text-coral"
                      : "border-transparent text-gray-400 hover:text-gray-600"
                  )}
                >
                  <Icon className="h-3.5 w-3.5" />
                  {tab.label}
                </Link>
              );
            })}
          </nav>
        </div>
      )}

      {children}
    </div>
  );
}
