"use client";

import { useState } from "react";
import { Bot, MessageCircle, HelpCircle, Megaphone, Play, Pause } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge, type StatusVariant } from "@/components/ui/status-badge";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { Modal } from "@/components/ui/modal";
import { toast } from "@/lib/toast-store";
import { cn } from "@/lib/utils";

type AutoMessageType = "welcome" | "suggested_questions" | "chat_prompts";

interface WelcomeMessage { id: string; message: string; triggerCondition: string; status: "active" | "paused"; sentCount: number; }
interface SuggestedQuestion { id: string; question: string; answer: string; clickCount: number; status: "active" | "paused"; }
interface ChatPrompt { id: string; title: string; message: string; schedule: string; targetAudience: string; status: "active" | "paused"; sentCount: number; }

const MOCK_WELCOME: WelcomeMessage[] = [
  { id: "wm-1", message: "Hi there! Thanks for visiting our store. How can we help you today?", triggerCondition: "First-time visitor", status: "active", sentCount: 4_560 },
  { id: "wm-2", message: "Welcome back! We have new arrivals since your last visit. Check them out!", triggerCondition: "Returning customer", status: "active", sentCount: 2_340 },
  { id: "wm-3", message: "Hey! Looks like you left something in your cart. Need help completing your purchase?", triggerCondition: "Abandoned cart (24h)", status: "active", sentCount: 890 },
  { id: "wm-4", message: "Thank you for your recent purchase! How are you enjoying your new product?", triggerCondition: "Post-purchase (7 days)", status: "paused", sentCount: 567 },
];

const MOCK_QUESTIONS: SuggestedQuestion[] = [
  { id: "sq-1", question: "What are your shipping options?", answer: "We offer Standard (5-7 days), Express (2-3 days), and Next Day delivery.", clickCount: 1_230, status: "active" },
  { id: "sq-2", question: "How do I track my order?", answer: "You can track your order using the tracking link sent to your email or in your account dashboard.", clickCount: 980, status: "active" },
  { id: "sq-3", question: "What is your return policy?", answer: "We accept returns within 30 days of purchase. Items must be in original condition.", clickCount: 870, status: "active" },
  { id: "sq-4", question: "Do you ship internationally?", answer: "Yes! We ship to over 50 countries. Shipping times vary by destination.", clickCount: 650, status: "active" },
  { id: "sq-5", question: "How can I contact customer support?", answer: "You can reach us via this chat, email at support@store.com, or call us at 1-800-XXX.", clickCount: 420, status: "paused" },
];

const MOCK_PROMPTS: ChatPrompt[] = [
  { id: "cp-1", title: "Weekend Sale Reminder", message: "Don't miss our weekend flash sale! Up to 50% off selected items.", schedule: "Every Friday 10:00 AM", targetAudience: "All subscribers", status: "active", sentCount: 3_200 },
  { id: "cp-2", title: "New Product Alert", message: "We just launched something you're going to love! Check out our latest collection.", schedule: "On new product publish", targetAudience: "Engaged customers", status: "active", sentCount: 1_800 },
  { id: "cp-3", title: "Review Request", message: "How was your recent order? We'd love to hear your feedback!", schedule: "14 days post-purchase", targetAudience: "Recent buyers", status: "active", sentCount: 950 },
  { id: "cp-4", title: "Re-engagement", message: "We miss you! Come back and enjoy 10% off your next order.", schedule: "30 days inactive", targetAudience: "Lapsed customers", status: "paused", sentCount: 450 },
];

const STATUS_VARIANT: Record<string, StatusVariant> = { active: "active", paused: "paused" };

export default function AutoMessagesPage() {
  const [tab, setTab] = useState<AutoMessageType>("welcome");
  const [showCreate, setShowCreate] = useState(false);

  const totalSent = MOCK_WELCOME.reduce((s, w) => s + w.sentCount, 0) + MOCK_PROMPTS.reduce((s, p) => s + p.sentCount, 0);
  const activeWelcome = MOCK_WELCOME.filter((w) => w.status === "active").length;
  const totalClicks = MOCK_QUESTIONS.reduce((s, q) => s + q.clickCount, 0);

  const welcomeColumns: Column<WelcomeMessage>[] = [
    {
      key: "message",
      header: "Message",
      render: (row) => (
        <div>
          <p className="text-xs font-medium text-gray-500 mb-1">Trigger: {row.triggerCondition}</p>
          <p className="text-sm text-gray-900 bg-gray-50 rounded-lg px-3 py-2">{row.message}</p>
        </div>
      ),
    },
    { key: "sent", header: "Sent", render: (row) => <span className="text-sm tabular-nums">{row.sentCount.toLocaleString()}</span> },
    { key: "status", header: "Status", render: (row) => <StatusBadge variant={STATUS_VARIANT[row.status] || "draft"} label={row.status} /> },
  ];

  const questionColumns: Column<SuggestedQuestion>[] = [
    {
      key: "question",
      header: "Question",
      render: (row) => (
        <div>
          <p className="text-sm font-medium text-gray-900">{row.question}</p>
          <p className="text-xs text-gray-500 mt-0.5">{row.answer}</p>
        </div>
      ),
    },
    { key: "clicks", header: "Clicks", render: (row) => <span className="text-sm tabular-nums">{row.clickCount.toLocaleString()}</span> },
    { key: "status", header: "Status", render: (row) => <StatusBadge variant={STATUS_VARIANT[row.status] || "draft"} label={row.status} /> },
  ];

  const promptColumns: Column<ChatPrompt>[] = [
    {
      key: "prompt",
      header: "Prompt",
      render: (row) => (
        <div>
          <p className="text-sm font-medium text-gray-900">{row.title}</p>
          <p className="text-xs text-gray-500 mt-0.5">{row.message}</p>
          <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
            <span>Schedule: {row.schedule}</span>
            <span>Audience: {row.targetAudience}</span>
          </div>
        </div>
      ),
    },
    { key: "sent", header: "Sent", render: (row) => <span className="text-sm tabular-nums">{row.sentCount.toLocaleString()}</span> },
    { key: "status", header: "Status", render: (row) => <StatusBadge variant={STATUS_VARIANT[row.status] || "draft"} label={row.status} /> },
  ];

  function handleCreate() {
    toast.success("Auto-message created successfully");
    setShowCreate(false);
  }

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard label="Total Sent" value={totalSent.toLocaleString()} icon={Bot} />
          <MetricCard label="Active Welcome" value={activeWelcome} icon={MessageCircle} />
          <MetricCard label="FAQ Clicks" value={totalClicks.toLocaleString()} icon={HelpCircle} />
          <MetricCard label="Active Prompts" value={MOCK_PROMPTS.filter((p) => p.status === "active").length} icon={Megaphone} />
        </MetricBar>
      }
      aside={
        <InsightPanel>
          <InsightItem title="Best performer" description="'First-time visitor' welcome message has highest send count (4,560). Consider A/B testing variations." variant="success" />
          <InsightItem title="Paused messages" description="1 welcome message and 1 prompt are paused. Review and reactivate if relevant." variant="warning" />
        </InsightPanel>
      }
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex gap-2">
          {([
            { key: "welcome" as const, label: "Welcome Messages", icon: MessageCircle },
            { key: "suggested_questions" as const, label: "Suggested Questions", icon: HelpCircle },
            { key: "chat_prompts" as const, label: "Chat Prompts", icon: Megaphone },
          ]).map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors",
                tab === t.key ? "bg-gray-900 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              )}
            >
              <t.icon className="h-3.5 w-3.5" />
              {t.label}
            </button>
          ))}
        </div>
        <button onClick={() => setShowCreate(true)} className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 transition-colors">
          Add New
        </button>
      </div>

      {tab === "welcome" && (
        <DataTable columns={welcomeColumns} data={MOCK_WELCOME} keyExtractor={(row) => row.id} emptyTitle="No welcome messages" emptyDescription="Create a welcome message to greet customers" />
      )}
      {tab === "suggested_questions" && (
        <DataTable columns={questionColumns} data={MOCK_QUESTIONS} keyExtractor={(row) => row.id} emptyTitle="No suggested questions" emptyDescription="Add FAQ questions for quick customer help" />
      )}
      {tab === "chat_prompts" && (
        <DataTable columns={promptColumns} data={MOCK_PROMPTS} keyExtractor={(row) => row.id} emptyTitle="No chat prompts" emptyDescription="Create chat prompts to engage customers" />
      )}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title={`New ${tab === "welcome" ? "Welcome Message" : tab === "suggested_questions" ? "Suggested Question" : "Chat Prompt"}`}>
        <div className="space-y-4">
          {tab === "suggested_questions" && (
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Question *</label>
              <input type="text" placeholder="Question text" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
            </div>
          )}
          {tab === "chat_prompts" && (
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Title *</label>
              <input type="text" placeholder="Prompt title" className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
            </div>
          )}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">{tab === "suggested_questions" ? "Answer" : "Message"} *</label>
            <textarea placeholder={tab === "suggested_questions" ? "Answer text" : "Message content"} rows={3} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none resize-none" />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button onClick={() => setShowCreate(false)} className="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50">Cancel</button>
            <button onClick={handleCreate} className="px-4 py-2 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90">Create</button>
          </div>
        </div>
      </Modal>
    </PageShell>
  );
}
