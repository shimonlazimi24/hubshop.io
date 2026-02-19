"use client";

import { motion } from "framer-motion";
import { Sparkles, Clock, TrendingUp, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

const valueProps = [
  { icon: Clock, text: "Save 10+ hours/week" },
  { icon: TrendingUp, text: "Scale across all TikTok channels" },
  { icon: Zap, text: "Launch campaigns in minutes" },
];

export function Hero() {
  return (
    <section className="relative min-h-screen overflow-hidden pt-28 pb-20">
      {/* Background gradient mesh */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 left-1/4 h-[600px] w-[600px] rounded-full bg-coral/10 blur-[120px]" />
        <div className="absolute top-20 right-1/4 h-[500px] w-[500px] rounded-full bg-cyan/10 blur-[120px]" />
        <div className="absolute bottom-0 left-1/2 h-[400px] w-[400px] -translate-x-1/2 rounded-full bg-purple/8 blur-[100px]" />
      </div>

      <div className="grain-overlay absolute inset-0 -z-10" />

      <div className="mx-auto max-w-7xl px-6">
        <div className="grid items-center gap-16 lg:grid-cols-2">
          {/* Left content */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: "easeOut" }}
            className="flex flex-col items-start"
          >
            <Badge className="mb-6">
              <Sparkles className="h-3.5 w-3.5 text-coral" />
              All-in-one TikTok platform
            </Badge>

            <h1 className="text-5xl font-extrabold leading-[1.1] tracking-tight text-foreground sm:text-6xl lg:text-7xl">
              Your Entire TikTok Business.{" "}
              <span className="gradient-text">One Platform.</span>
            </h1>

            <p className="mt-6 max-w-lg text-lg leading-relaxed text-foreground-secondary">
              Connect TikTok Shop, Ads, and Creator tools in one dashboard.
              Manage everything from orders to campaigns — no more switching
              between platforms.
            </p>

            <div className="mt-8 flex flex-col gap-3">
              {valueProps.map((prop) => (
                <div key={prop.text} className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg gradient-bg">
                    <prop.icon className="h-4 w-4 text-white" />
                  </div>
                  <span className="text-sm font-medium text-foreground">
                    {prop.text}
                  </span>
                </div>
              ))}
            </div>

            <div className="mt-10 flex flex-wrap items-center gap-4">
              <Link href="/register">
                <Button variant="gradient" size="lg">
                  Get Started Free
                </Button>
              </Link>
              <Button variant="outline" size="lg">
                Watch Demo
              </Button>
            </div>
          </motion.div>

          {/* Right - Dashboard mockup */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
            className="relative hidden lg:block"
          >
            <motion.div
              animate={{ y: [0, -12, 0] }}
              transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
              className="relative"
            >
              {/* Main dashboard card */}
              <div className="rounded-2xl border border-border bg-white p-6 shadow-2xl shadow-foreground/5">
                <div className="mb-4 flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-coral" />
                  <div className="h-3 w-3 rounded-full bg-cyan" />
                  <div className="h-3 w-3 rounded-full bg-purple" />
                </div>
                <div className="space-y-3">
                  <div className="h-8 w-3/4 rounded-lg bg-surface" />
                  <div className="grid grid-cols-3 gap-3">
                    <div className="h-20 rounded-xl bg-coral/10" />
                    <div className="h-20 rounded-xl bg-cyan/10" />
                    <div className="h-20 rounded-xl bg-purple/10" />
                  </div>
                  <div className="h-32 rounded-xl bg-surface" />
                  <div className="grid grid-cols-2 gap-3">
                    <div className="h-16 rounded-xl bg-surface" />
                    <div className="h-16 rounded-xl bg-surface" />
                  </div>
                </div>
              </div>

              {/* Floating notification card */}
              <motion.div
                animate={{ y: [0, -6, 0] }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 1,
                }}
                className="absolute -left-8 bottom-20 rounded-xl border border-border bg-white p-4 shadow-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100">
                    <TrendingUp className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-foreground">
                      Revenue up 384%
                    </p>
                    <p className="text-xs text-foreground-secondary">
                      Last 30 days
                    </p>
                  </div>
                </div>
              </motion.div>

              {/* Floating order card */}
              <motion.div
                animate={{ y: [0, -8, 0] }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 0.5,
                }}
                className="absolute -right-4 top-12 rounded-xl border border-border bg-white p-4 shadow-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-coral/10">
                    <Zap className="h-5 w-5 text-coral" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-foreground">
                      New order #4,821
                    </p>
                    <p className="text-xs text-foreground-secondary">
                      Just now
                    </p>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
