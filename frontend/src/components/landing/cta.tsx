"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export function CTA() {
  return (
    <section className="relative overflow-hidden py-24">
      {/* Background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 gradient-bg opacity-[0.06]" />
        <div className="absolute top-0 left-1/4 h-[400px] w-[400px] rounded-full bg-coral/10 blur-[100px]" />
        <div className="absolute bottom-0 right-1/4 h-[400px] w-[400px] rounded-full bg-cyan/10 blur-[100px]" />
      </div>

      <div className="mx-auto max-w-4xl px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            Ready to Unify Your{" "}
            <span className="gradient-text">TikTok Business?</span>
          </h2>
          <p className="mx-auto mt-6 max-w-xl text-lg text-foreground-secondary">
            Join thousands of sellers who manage everything from one platform.
            Free to start, no credit card required.
          </p>

          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link href="/register">
              <Button variant="gradient" size="lg">
                Get Started Free
              </Button>
            </Link>
          </div>
          <p className="mt-4 text-sm text-foreground-secondary">
            No credit card required &middot; Free plan available
          </p>
        </motion.div>

        {/* Floating decorative elements */}
        <div className="pointer-events-none absolute inset-0">
          <motion.div
            animate={{ y: [0, -10, 0], rotate: [0, 5, 0] }}
            transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
            className="absolute left-[10%] top-[20%] h-16 w-24 rounded-xl border border-border/50 bg-white/60 shadow-sm backdrop-blur"
          />
          <motion.div
            animate={{ y: [0, 10, 0], rotate: [0, -3, 0] }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 1,
            }}
            className="absolute right-[10%] top-[30%] h-12 w-20 rounded-xl border border-border/50 bg-white/60 shadow-sm backdrop-blur"
          />
          <motion.div
            animate={{ y: [0, -8, 0] }}
            transition={{
              duration: 7,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 2,
            }}
            className="absolute left-[15%] bottom-[15%] h-10 w-16 rounded-lg border border-border/50 bg-white/60 shadow-sm backdrop-blur"
          />
          <motion.div
            animate={{ y: [0, 12, 0] }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 0.5,
            }}
            className="absolute right-[15%] bottom-[20%] h-14 w-14 rounded-xl border border-border/50 bg-white/60 shadow-sm backdrop-blur"
          />
        </div>
      </div>
    </section>
  );
}
