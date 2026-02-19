"use client";

import { motion } from "framer-motion";
import { Link2, LayoutDashboard, Rocket } from "lucide-react";

const steps = [
  {
    number: "01",
    icon: Link2,
    title: "Connect",
    description:
      "Link your TikTok Shop, Ads, and Developer accounts with one-click OAuth. Setup takes under 5 minutes.",
    color: "coral",
  },
  {
    number: "02",
    icon: LayoutDashboard,
    title: "Manage",
    description:
      "See all orders, campaigns, content, and analytics in one unified dashboard. No more tab-switching.",
    color: "purple",
  },
  {
    number: "03",
    icon: Rocket,
    title: "Scale",
    description:
      "Launch campaigns, find creators, and grow your business with AI-powered tools and unified insights.",
    color: "cyan",
  },
];

const colorMap: Record<string, string> = {
  coral: "bg-coral/10 text-coral border-coral/20",
  purple: "bg-purple/10 text-purple border-purple/20",
  cyan: "bg-cyan/10 text-cyan border-cyan/20",
};

const numberColor: Record<string, string> = {
  coral: "text-coral",
  purple: "text-purple",
  cyan: "text-cyan",
};

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            Up and Running in{" "}
            <span className="gradient-text">3 Steps</span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-foreground-secondary">
            Getting started with Frodo is fast and simple. Connect your accounts
            and start managing everything from day one.
          </p>
        </motion.div>

        <div className="mt-16 grid gap-8 md:grid-cols-3">
          {steps.map((step, index) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              className="relative rounded-2xl border border-border bg-white p-8"
            >
              <span
                className={`text-5xl font-extrabold ${numberColor[step.color]} opacity-20`}
              >
                {step.number}
              </span>
              <div
                className={`mt-4 mb-5 inline-flex h-14 w-14 items-center justify-center rounded-xl border ${colorMap[step.color]}`}
              >
                <step.icon className="h-7 w-7" />
              </div>
              <h3 className="text-xl font-bold text-foreground">
                {step.title}
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-foreground-secondary">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
