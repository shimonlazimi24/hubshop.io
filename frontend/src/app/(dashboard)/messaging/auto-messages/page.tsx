"use client";

import { useState } from "react";
import {
  Bot,
  MessageCircle,
  HelpCircle,
  Megaphone,
  Play,
  Pause,
  Plus,
  X,
  Edit3,
} from "lucide-react";
import { cn } from "@/lib/utils";

type AutoMessageType = "welcome" | "suggested_questions" | "chat_prompts";

const TABS: { key: AutoMessageType; label: string; icon: typeof Bot }[] = [
  { key: "welcome", label: "Welcome Messages", icon: MessageCircle },
  { key: "suggested_questions", label: "Suggested Questions", icon: HelpCircle },
  { key: "chat_prompts", label: "Chat Prompts", icon: Megaphone },
];

interface WelcomeMessage {
  id: string;
  message: string;
  triggerCondition: string;
  status: "active" | "paused";
  sentCount: number;
}

const MOCK_WELCOME: WelcomeMessage[] = [
  {
    id: "wm-1",
    message: "Hi there! Thanks for visiting our store. How can we help you today?",
    triggerCondition: "First-time visitor",
    status: "active",
    sentCount: 4_560,
  },
  {
    id: "wm-2",
    message: "Welcome back! We have new arrivals since your last visit. Check them out!",
    triggerCondition: "Returning customer",
    status: "active",
    sentCount: 2_340,
  },
  {
    id: "wm-3",
    message: "Hey! Looks like you left something in your cart. Need help completing your purchase?",
    triggerCondition: "Abandoned cart (24h)",
    status: "active",
    sentCount: 890,
  },
  {
    id: "wm-4",
    message: "Thank you for your recent purchase! How are you enjoying your new product?",
    triggerCondition: "Post-purchase (7 days)",
    status: "paused",
    sentCount: 567,
  },
];

interface SuggestedQuestion {
  id: string;
  question: string;
  answer: string;
  clickCount: number;
  status: "active" | "paused";
}

const MOCK_QUESTIONS: SuggestedQuestion[] = [
  {
    id: "sq-1",
    question: "What are your shipping options?",
    answer: "We offer Standard (5-7 days), Express (2-3 days), and Next Day delivery.",
    clickCount: 1_230,
    status: "active",
  },
  {
    id: "sq-2",
    question: "How do I track my order?",
    answer: "You can track your order using the tracking link sent to your email or in your account dashboard.",
    clickCount: 980,
    status: "active",
  },
  {
    id: "sq-3",
    question: "What is your return policy?",
    answer: "We accept returns within 30 days of purchase. Items must be in original condition.",
    clickCount: 870,
    status: "active",
  },
  {
    id: "sq-4",
    question: "Do you ship internationally?",
    answer: "Yes! We ship to over 50 countries. Shipping times vary by destination.",
    clickCount: 650,
    status: "active",
  },
  {
    id: "sq-5",
    question: "How can I contact customer support?",
    answer: "You can reach us via this chat, email at support@store.com, or call us at 1-800-XXX.",
    clickCount: 420,
    status: "paused",
  },
];

interface ChatPrompt {
  id: string;
  title: string;
  message: string;
  schedule: string;
  targetAudience: string;
  status: "active" | "paused";
  sentCount: number;
}

const MOCK_PROMPTS: ChatPrompt[] = [
  {
    id: "cp-1",
    title: "Weekend Sale Reminder",
    message: "Don't miss our weekend flash sale! Up to 50% off selected items.",
    schedule: "Every Friday 10:00 AM",
    targetAudience: "All subscribers",
    status: "active",
    sentCount: 3_200,
  },
  {
    id: "cp-2",
    title: "New Product Alert",
    message: "We just launched something you're going to love! Check out our latest collection.",
    schedule: "On new product publish",
    targetAudience: "Engaged customers",
    status: "active",
    sentCount: 1_800,
  },
  {
    id: "cp-3",
    title: "Review Request",
    message: "How was your recent order? We'd love to hear your feedback!",
    schedule: "14 days post-purchase",
    targetAudience: "Recent buyers",
    status: "active",
    sentCount: 950,
  },
  {
    id: "cp-4",
    title: "Re-engagement",
    message: "We miss you! Come back and enjoy 10% off your next order.",
    schedule: "30 days inactive",
    targetAudience: "Lapsed customers",
    status: "paused",
    sentCount: 450,
  },
];

export default function AutoMessagesPage() {
  const [tab, setTab] = useState<AutoMessageType>("welcome");
  const [showCreate, setShowCreate] = useState(false);

  return (
    <div className="max-w-6xl">
      {/* Tab Switcher */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex gap-2">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => { setTab(t.key); setShowCreate(false); }}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors",
                tab === t.key
                  ? "bg-gray-900 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              )}
            >
              <t.icon className="h-3.5 w-3.5" />
              {t.label}
            </button>
          ))}
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="flex items-center gap-1.5 rounded-lg bg-coral px-3 py-2 text-sm font-medium text-white hover:bg-coral/90 transition-colors"
        >
          {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showCreate ? "Cancel" : "Add New"}
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="rounded-xl border border-gray-100 bg-white p-5 mb-6">
          <h3 className="text-sm font-medium text-gray-900 mb-3">
            New {tab === "welcome" ? "Welcome Message" : tab === "suggested_questions" ? "Suggested Question" : "Chat Prompt"}
          </h3>
          <div className="space-y-3">
            {tab === "suggested_questions" && (
              <input
                type="text"
                placeholder="Question text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              />
            )}
            {tab === "chat_prompts" && (
              <input
                type="text"
                placeholder="Prompt title"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              />
            )}
            <textarea
              placeholder={tab === "suggested_questions" ? "Answer text" : "Message content"}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm resize-none"
            />
            <button className="px-4 py-2 bg-gray-900 text-white rounded-md text-sm font-medium hover:bg-gray-800">
              Create
            </button>
          </div>
        </div>
      )}

      {/* Welcome Messages Tab */}
      {tab === "welcome" && (
        <div className="space-y-3">
          {MOCK_WELCOME.map((wm) => (
            <div
              key={wm.id}
              className="rounded-xl border border-gray-100 bg-white p-5"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
                    <Bot className="h-4 w-4 text-blue-500" />
                  </div>
                  <div>
                    <span className="text-xs font-medium text-gray-500">
                      Trigger: {wm.triggerCondition}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">
                    {wm.sentCount.toLocaleString()} sent
                  </span>
                  <span
                    className={cn(
                      "inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full",
                      wm.status === "active"
                        ? "bg-green-100 text-green-700"
                        : "bg-gray-100 text-gray-600"
                    )}
                  >
                    {wm.status === "active" ? (
                      <Play className="h-3 w-3" />
                    ) : (
                      <Pause className="h-3 w-3" />
                    )}
                    {wm.status === "active" ? "Active" : "Paused"}
                  </span>
                </div>
              </div>
              <p className="text-sm text-gray-900 bg-gray-50 rounded-lg px-3 py-2">
                {wm.message}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Suggested Questions Tab */}
      {tab === "suggested_questions" && (
        <div className="bg-white rounded-lg border border-gray-200">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 text-left">
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Question</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Clicks</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase w-16">Edit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {MOCK_QUESTIONS.map((q) => (
                <tr key={q.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="flex items-start gap-2">
                      <HelpCircle className="h-4 w-4 text-purple mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{q.question}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{q.answer}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {q.clickCount.toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={cn(
                        "inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full",
                        q.status === "active"
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-600"
                      )}
                    >
                      {q.status === "active" ? "Active" : "Paused"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button className="text-gray-400 hover:text-gray-600">
                      <Edit3 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Chat Prompts Tab */}
      {tab === "chat_prompts" && (
        <div className="space-y-3">
          {MOCK_PROMPTS.map((prompt) => (
            <div
              key={prompt.id}
              className="rounded-xl border border-gray-100 bg-white p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Megaphone className="h-4 w-4 text-coral" />
                  <h3 className="text-sm font-semibold text-gray-900">{prompt.title}</h3>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">
                    {prompt.sentCount.toLocaleString()} sent
                  </span>
                  <span
                    className={cn(
                      "inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full",
                      prompt.status === "active"
                        ? "bg-green-100 text-green-700"
                        : "bg-gray-100 text-gray-600"
                    )}
                  >
                    {prompt.status === "active" ? (
                      <Play className="h-3 w-3" />
                    ) : (
                      <Pause className="h-3 w-3" />
                    )}
                    {prompt.status === "active" ? "Active" : "Paused"}
                  </span>
                </div>
              </div>
              <p className="text-sm text-gray-700 bg-gray-50 rounded-lg px-3 py-2 mb-2">
                {prompt.message}
              </p>
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span>Schedule: {prompt.schedule}</span>
                <span>Audience: {prompt.targetAudience}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
