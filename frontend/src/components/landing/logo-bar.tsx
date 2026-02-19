"use client";

import { motion } from "framer-motion";

const brands = [
  "StyleCo",
  "FreshGoods",
  "VibeBrand",
  "NovaShop",
  "PeakSellers",
  "GlowLab",
  "TrendHive",
  "UrbanPick",
  "ShopWave",
  "PixelMart",
];

export function LogoBar() {
  return (
    <section className="border-y border-border bg-surface-alt py-12">
      <div className="mx-auto max-w-7xl px-6">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="mb-8 text-center text-sm font-medium text-foreground-secondary"
        >
          Trusted by 2,000+ TikTok sellers and brands
        </motion.p>

        <div className="relative overflow-hidden">
          {/* Fade edges */}
          <div className="pointer-events-none absolute left-0 top-0 z-10 h-full w-24 bg-gradient-to-r from-surface-alt to-transparent" />
          <div className="pointer-events-none absolute right-0 top-0 z-10 h-full w-24 bg-gradient-to-l from-surface-alt to-transparent" />

          <div className="flex animate-scroll-logos gap-16">
            {[...brands, ...brands].map((brand, i) => (
              <div
                key={`${brand}-${i}`}
                className="flex shrink-0 items-center justify-center grayscale opacity-40 transition-all duration-300 hover:opacity-100 hover:grayscale-0"
              >
                <div className="flex h-10 items-center gap-2 rounded-lg px-4">
                  <div className="h-6 w-6 rounded-md bg-foreground/20" />
                  <span className="whitespace-nowrap text-base font-semibold text-foreground/50">
                    {brand}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
