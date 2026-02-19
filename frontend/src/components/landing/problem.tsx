"use client";

import { motion } from "framer-motion";
import {
  ShoppingBag,
  Megaphone,
  Users,
  X,
  Check,
  ArrowRight,
} from "lucide-react";

const painPoints = [
  {
    icon: ShoppingBag,
    platform: "TikTok Shop",
    pains: ["Order management", "Product sync", "Fulfillment tracking"],
    color: "coral",
  },
  {
    icon: Megaphone,
    platform: "TikTok Ads Manager",
    pains: ["Campaign setup", "Audience targeting", "Budget optimization"],
    color: "purple",
  },
  {
    icon: Users,
    platform: "Creator Marketplace",
    pains: ["Finding influencers", "Managing collabs", "Tracking ROI"],
    color: "cyan",
  },
];

const colorMap: Record<string, string> = {
  coral: "bg-coral/10 text-coral",
  purple: "bg-purple/10 text-purple",
  cyan: "bg-cyan/10 text-cyan",
};

export function Problem() {
  return (
    <section className="py-24">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            Stop Juggling{" "}
            <span className="gradient-text">3 Different Platforms</span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-foreground-secondary">
            Managing TikTok Shop, Ads, and Creators across separate dashboards
            wastes hours every day. Frodo brings it all together.
          </p>
        </motion.div>

        <div className="mt-16 grid gap-8 md:grid-cols-3">
          {painPoints.map((point, index) => (
            <motion.div
              key={point.platform}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: index * 0.15 }}
              className="rounded-2xl border border-border bg-white p-8"
            >
              <div
                className={`mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl ${colorMap[point.color]}`}
              >
                <point.icon className="h-6 w-6" />
              </div>

              <h3 className="mb-4 text-lg font-semibold text-foreground">
                {point.platform}
              </h3>

              <div className="space-y-3">
                {point.pains.map((pain) => (
                  <div
                    key={pain}
                    className="flex items-center gap-2 text-sm text-foreground-secondary"
                  >
                    <X className="h-4 w-4 shrink-0 text-red-400" />
                    <span>{pain}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-12 flex flex-col items-center gap-4 sm:flex-row sm:justify-center"
        >
          <ArrowRight className="h-6 w-6 rotate-90 text-foreground-secondary sm:rotate-0" />
          <div className="flex items-center gap-2 rounded-full bg-green-50 px-6 py-3">
            <Check className="h-5 w-5 text-green-600" />
            <span className="text-sm font-semibold text-green-700">
              Frodo unifies all three into one platform
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
