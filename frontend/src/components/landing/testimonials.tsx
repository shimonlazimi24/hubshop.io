"use client";

import { motion } from "framer-motion";
import { Star } from "lucide-react";

const testimonials = [
  {
    quote:
      "Frodo cut our daily TikTok management from 4 hours to 45 minutes. We finally have one place for orders, ads, and creator collabs.",
    name: "Sarah Chen",
    role: "Head of E-Commerce",
    company: "GlowBeauty Co.",
    avatar: "SC",
  },
  {
    quote:
      "We scaled from $10K to $150K monthly GMV in 3 months. The unified analytics helped us double down on what actually works.",
    name: "Marcus Johnson",
    role: "Founder & CEO",
    company: "UrbanFit Apparel",
    avatar: "MJ",
  },
  {
    quote:
      "Managing 50+ creator partnerships was a nightmare before Frodo. Now we track everything — from seeding to sales — in one dashboard.",
    name: "Elena Rodriguez",
    role: "Creator Partnerships Lead",
    company: "FreshBite Foods",
    avatar: "ER",
  },
];

export function Testimonials() {
  return (
    <section className="bg-surface-alt py-24">
      <div className="mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            Loved by <span className="gradient-text">TikTok Sellers</span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-foreground-secondary">
            See how businesses like yours are growing with Frodo.
          </p>
        </motion.div>

        <div className="mt-16 grid gap-8 md:grid-cols-3">
          {testimonials.map((t, index) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: index * 0.15 }}
              whileHover={{ y: -4 }}
              className="rounded-2xl border border-border bg-white p-8 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="mb-4 flex gap-1">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star
                    key={i}
                    className="h-4 w-4 fill-amber-400 text-amber-400"
                  />
                ))}
              </div>

              <blockquote className="text-sm leading-relaxed text-foreground-secondary">
                &ldquo;{t.quote}&rdquo;
              </blockquote>

              <div className="mt-6 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full gradient-bg text-xs font-bold text-white">
                  {t.avatar}
                </div>
                <div>
                  <p className="text-sm font-semibold text-foreground">
                    {t.name}
                  </p>
                  <p className="text-xs text-foreground-secondary">
                    {t.role}, {t.company}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
