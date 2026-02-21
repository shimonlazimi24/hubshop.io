"use client";

import { Play, Image, LayoutGrid } from "lucide-react";
import { cn } from "@/lib/utils";

type CreativeFormat = "video" | "image" | "carousel";

const FORMAT_CONFIG: Record<CreativeFormat, { icon: typeof Play; label: string; color: string }> = {
  video: { icon: Play, label: "Video", color: "bg-coral/80 text-white" },
  image: { icon: Image, label: "Image", color: "bg-purple/80 text-white" },
  carousel: { icon: LayoutGrid, label: "Carousel", color: "bg-cyan/80 text-white" },
};

interface CreativeMetric {
  label: string;
  value: string;
}

interface CreativeCardProps {
  title: string;
  thumbnailUrl?: string;
  format: CreativeFormat;
  metrics?: CreativeMetric[];
  onClick?: () => void;
  className?: string;
}

export function CreativeCard({
  title,
  thumbnailUrl,
  format,
  metrics = [],
  onClick,
  className,
}: CreativeCardProps) {
  const config = FORMAT_CONFIG[format];
  const FormatIcon = config.icon;

  return (
    <div
      onClick={onClick}
      className={cn(
        "group rounded-xl border border-gray-100 bg-white overflow-hidden shadow-[var(--shadow-card)] transition-all duration-[var(--duration-fast)] hover:shadow-[var(--shadow-panel)]",
        onClick && "cursor-pointer",
        className
      )}
    >
      {/* Thumbnail */}
      <div className="relative aspect-[9/16] max-h-48 bg-gray-100 overflow-hidden">
        {thumbnailUrl ? (
          <img src={thumbnailUrl} alt={title} className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <FormatIcon className="h-8 w-8 text-gray-300" />
          </div>
        )}

        {/* Format badge */}
        <span
          className={cn(
            "absolute top-2 left-2 inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-[10px] font-semibold",
            config.color
          )}
        >
          <FormatIcon className="h-3 w-3" />
          {config.label}
        </span>

        {/* Hover overlay with play button for videos */}
        {format === "video" && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/0 group-hover:bg-black/20 transition-colors">
            <div className="h-10 w-10 flex items-center justify-center rounded-full bg-white/90 opacity-0 group-hover:opacity-100 transition-opacity shadow-lg">
              <Play className="h-4 w-4 text-gray-900 ml-0.5" />
            </div>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-3">
        <h4 className="text-sm font-medium text-gray-900 truncate mb-2">{title}</h4>
        {metrics.length > 0 && (
          <div className="flex flex-wrap gap-x-4 gap-y-1">
            {metrics.map((m) => (
              <div key={m.label} className="text-center">
                <p className="text-xs font-semibold text-gray-900 tabular-nums">{m.value}</p>
                <p className="text-[10px] text-gray-400">{m.label}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
