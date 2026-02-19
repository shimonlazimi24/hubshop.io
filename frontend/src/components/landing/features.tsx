"use client";

import { motion } from "framer-motion";
import {
  ShoppingCart,
  Megaphone,
  Video,
  Users,
  BarChart3,
  Package,
  Target,
  Calendar,
  Handshake,
  PieChart,
  TrendingUp,
} from "lucide-react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

const features = [
  {
    id: "commerce",
    label: "Commerce",
    icon: ShoppingCart,
    title: "Unified Commerce Hub",
    description:
      "Manage your entire TikTok Shop from one dashboard. Sync products, track orders, and handle fulfillment without switching tabs.",
    bullets: [
      { icon: Package, text: "Real-time order management & fulfillment" },
      { icon: ShoppingCart, text: "Product catalog sync across regions" },
      { icon: BarChart3, text: "Inventory tracking & low-stock alerts" },
      { icon: Target, text: "GMV analytics & revenue insights" },
    ],
    accent: "coral",
  },
  {
    id: "advertising",
    label: "Advertising",
    icon: Megaphone,
    title: "Smart Ad Management",
    description:
      "Build, launch, and optimize TikTok ad campaigns with AI-powered tools. From Spark Ads to GMV Max — all in one place.",
    bullets: [
      { icon: Target, text: "Campaign builder with audience targeting" },
      { icon: BarChart3, text: "Budget optimizer with ROAS tracking" },
      { icon: Megaphone, text: "Spark Ads & GMV Max integration" },
      { icon: PieChart, text: "Cross-campaign performance analytics" },
    ],
    accent: "purple",
  },
  {
    id: "content",
    label: "Content",
    icon: Video,
    title: "Content Command Center",
    description:
      "Schedule, publish, and track your TikTok content performance. Manage your video library and optimize posting strategy.",
    bullets: [
      { icon: Video, text: "Video library & content management" },
      { icon: Calendar, text: "Smart scheduling & auto-publishing" },
      { icon: BarChart3, text: "Performance tracking per video" },
      { icon: Target, text: "Trending sounds & hashtag insights" },
    ],
    accent: "cyan",
  },
  {
    id: "creators",
    label: "Creators",
    icon: Users,
    title: "Creator Collaboration",
    description:
      "Find the perfect creators for your brand. Manage partnerships, track deliverables, and measure creator-driven revenue.",
    bullets: [
      { icon: Users, text: "Creator discovery with smart filters" },
      { icon: Handshake, text: "Collaboration management & contracts" },
      { icon: Package, text: "Product seeding & sample tracking" },
      { icon: BarChart3, text: "Creator ROI & attribution analytics" },
    ],
    accent: "purple",
  },
  {
    id: "analytics",
    label: "Analytics",
    icon: BarChart3,
    title: "Unified Analytics",
    description:
      "See everything in one place. Cross-platform metrics, custom reports, and actionable insights to grow your TikTok business.",
    bullets: [
      { icon: PieChart, text: "Cross-platform unified dashboard" },
      { icon: BarChart3, text: "Custom report builder & exports" },
      { icon: Target, text: "Conversion funnel analysis" },
      { icon: TrendingUp, text: "Growth trends & forecasting" },
    ],
    accent: "coral",
  },
];

const accentMap: Record<string, string> = {
  coral: "bg-coral/10 text-coral",
  purple: "bg-purple/10 text-purple",
  cyan: "bg-cyan/10 text-cyan",
};

const mockupAccent: Record<string, string> = {
  coral: "bg-coral/5",
  purple: "bg-purple/5",
  cyan: "bg-cyan/5",
};

export function Features() {
  return (
    <section id="features" className="bg-surface-alt py-24">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            Everything You Need,{" "}
            <span className="gradient-text">One Dashboard</span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-foreground-secondary">
            Five powerful modules working together to run your entire TikTok
            business.
          </p>
        </motion.div>

        <div className="mt-14">
          <Tabs defaultValue="commerce" className="flex flex-col items-center">
            <TabsList className="flex-wrap justify-center">
              {features.map((f) => (
                <TabsTrigger key={f.id} value={f.id}>
                  <span className="flex items-center gap-2">
                    <f.icon className="h-4 w-4" />
                    {f.label}
                  </span>
                </TabsTrigger>
              ))}
            </TabsList>

            {features.map((f) => (
                <TabsContent key={f.id} value={f.id}>
                  <div className="grid items-center gap-12 lg:grid-cols-2">
                    <div>
                      <div
                        className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl ${accentMap[f.accent]}`}
                      >
                        <f.icon className="h-6 w-6" />
                      </div>
                      <h3 className="text-2xl font-bold text-foreground">
                        {f.title}
                      </h3>
                      <p className="mt-3 text-foreground-secondary">
                        {f.description}
                      </p>
                      <div className="mt-6 space-y-4">
                        {f.bullets.map((b) => (
                          <div
                            key={b.text}
                            className="flex items-center gap-3"
                          >
                            <div
                              className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${accentMap[f.accent]}`}
                            >
                              <b.icon className="h-4 w-4" />
                            </div>
                            <span className="text-sm font-medium text-foreground">
                              {b.text}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Feature mockup */}
                    <div
                      className={`rounded-2xl border border-border p-8 ${mockupAccent[f.accent]}`}
                    >
                      <div className="space-y-4">
                        <div className="h-6 w-1/2 rounded-lg bg-foreground/5" />
                        <div className="grid grid-cols-2 gap-4">
                          <div className="h-24 rounded-xl bg-white shadow-sm" />
                          <div className="h-24 rounded-xl bg-white shadow-sm" />
                        </div>
                        <div className="h-40 rounded-xl bg-white shadow-sm" />
                        <div className="grid grid-cols-3 gap-3">
                          <div className="h-12 rounded-lg bg-white shadow-sm" />
                          <div className="h-12 rounded-lg bg-white shadow-sm" />
                          <div className="h-12 rounded-lg bg-white shadow-sm" />
                        </div>
                      </div>
                    </div>
                  </div>
                </TabsContent>
              ))}
          </Tabs>
        </div>
      </div>
    </section>
  );
}
