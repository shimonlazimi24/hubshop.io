"use client";

import { useState } from "react";
import { Upload, Video, Image, Hash, Calendar, Clock, Sparkles, X, Plus, Eye } from "lucide-react";
import { PageShell } from "@/components/ui/page-shell";
import { InsightPanel, InsightItem } from "@/components/ui/insight-panel";
import { cn } from "@/lib/utils";

type ContentType = "video" | "photo";

const RECOMMENDED_HASHTAGS = [
  { tag: "#skincare", relevance: 95 },
  { tag: "#beautytok", relevance: 92 },
  { tag: "#tiktokmademebuyit", relevance: 88 },
  { tag: "#skincareroutine", relevance: 85 },
  { tag: "#glowup", relevance: 82 },
  { tag: "#selfcare", relevance: 78 },
  { tag: "#beauty", relevance: 75 },
  { tag: "#fyp", relevance: 72 },
  { tag: "#viral", relevance: 68 },
  { tag: "#trending", relevance: 65 },
];

const BEST_TIMES = [
  { day: "Monday", time: "7:00 PM", engagement: "High" },
  { day: "Tuesday", time: "12:00 PM", engagement: "Medium" },
  { day: "Wednesday", time: "5:00 PM", engagement: "High" },
  { day: "Thursday", time: "3:00 PM", engagement: "Medium" },
  { day: "Friday", time: "6:00 PM", engagement: "Very High" },
  { day: "Saturday", time: "11:00 AM", engagement: "High" },
  { day: "Sunday", time: "10:00 AM", engagement: "Medium" },
];

export default function PublishPage() {
  const [contentType, setContentType] = useState<ContentType>("video");
  const [caption, setCaption] = useState("");
  const [selectedHashtags, setSelectedHashtags] = useState<string[]>([]);
  const [scheduleDate, setScheduleDate] = useState("");
  const [scheduleTime, setScheduleTime] = useState("");

  function toggleHashtag(tag: string) {
    setSelectedHashtags((prev) => prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]);
  }

  function addHashtagToCaption() {
    if (selectedHashtags.length === 0) return;
    const hashtagString = selectedHashtags.join(" ");
    setCaption((prev) => (prev ? `${prev}\n\n${hashtagString}` : hashtagString));
  }

  return (
    <PageShell
      aside={
        <InsightPanel>
          <InsightItem title="Hashtag strategy" description={`${selectedHashtags.length} hashtags selected. Optimal range is 3-5 for maximum reach.`} variant={selectedHashtags.length >= 3 && selectedHashtags.length <= 5 ? "success" : "default"} />
          <InsightItem title="Best time today" description="Friday 6:00 PM shows 'Very High' engagement based on your audience." variant="success" />
          <InsightItem title="Caption length" description={`${caption.length}/2,200 characters. Captions with 100-150 chars get the best engagement.`} />
        </InsightPanel>
      }
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Content Type */}
          <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-5">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">Content Type</h2>
            <div className="flex gap-3">
              <button
                onClick={() => setContentType("video")}
                className={cn("flex-1 flex items-center justify-center gap-2 rounded-lg border-2 p-4 transition-colors", contentType === "video" ? "border-coral bg-coral/5 text-coral" : "border-gray-200 text-gray-500 hover:border-gray-300")}
              >
                <Video className="h-5 w-5" />
                <span className="text-sm font-medium">Video</span>
              </button>
              <button
                onClick={() => setContentType("photo")}
                className={cn("flex-1 flex items-center justify-center gap-2 rounded-lg border-2 p-4 transition-colors", contentType === "photo" ? "border-coral bg-coral/5 text-coral" : "border-gray-200 text-gray-500 hover:border-gray-300")}
              >
                <Image className="h-5 w-5" />
                <span className="text-sm font-medium">Photo</span>
              </button>
            </div>
          </div>

          {/* Upload Area */}
          <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-5">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">Upload</h2>
            <div className="rounded-lg border-2 border-dashed border-gray-200 p-8 text-center hover:border-coral/50 hover:bg-coral/5 transition-colors cursor-pointer">
              <Upload className="h-10 w-10 text-gray-300 mx-auto mb-3" />
              <p className="text-sm font-medium text-gray-600">Drag and drop your {contentType} here</p>
              <p className="text-xs text-gray-400 mt-1">{contentType === "video" ? "MP4, MOV up to 500MB" : "JPG, PNG up to 20MB"}</p>
              <button className="mt-3 px-4 py-2 bg-gray-100 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-200 transition-colors">Browse Files</button>
            </div>
          </div>

          {/* Caption */}
          <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-gray-900">Caption</h2>
              <span className="text-xs text-gray-400">{caption.length}/2,200</span>
            </div>
            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="Write your caption here..."
              rows={5}
              maxLength={2200}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-coral/30 focus:border-coral"
            />
            {selectedHashtags.length > 0 && (
              <div className="mt-3">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs text-gray-500">Selected hashtags:</p>
                  <button onClick={addHashtagToCaption} className="text-xs text-coral font-medium hover:underline">Add to caption</button>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {selectedHashtags.map((tag) => (
                    <span key={tag} className="inline-flex items-center gap-1 px-2 py-1 bg-purple/10 text-purple rounded-full text-xs">
                      {tag}
                      <button onClick={() => toggleHashtag(tag)}><X className="h-3 w-3" /></button>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Schedule */}
          <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-5">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">Schedule</h2>
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div>
                <label className="text-xs text-gray-500 mb-1 block">Date</label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input type="date" value={scheduleDate} onChange={(e) => setScheduleDate(e.target.value)} className="w-full pl-10 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
                </div>
              </div>
              <div>
                <label className="text-xs text-gray-500 mb-1 block">Time</label>
                <div className="relative">
                  <Clock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input type="time" value={scheduleTime} onChange={(e) => setScheduleTime(e.target.value)} className="w-full pl-10 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-coral/30 focus:border-coral outline-none" />
                </div>
              </div>
            </div>
            <div className="flex gap-3">
              <button className="flex-1 px-4 py-2.5 bg-coral text-white rounded-lg text-sm font-medium hover:bg-coral/90 transition-colors">Publish Now</button>
              <button disabled={!scheduleDate || !scheduleTime} className="flex-1 px-4 py-2.5 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 disabled:opacity-50 transition-colors">Schedule</button>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Hashtag Recommendations */}
          <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-5">
            <h2 className="text-sm font-semibold text-gray-900 mb-1 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple" />
              Hashtag Recommendations
            </h2>
            <p className="text-xs text-gray-500 mb-4">AI-suggested hashtags based on your content</p>
            <div className="space-y-2">
              {RECOMMENDED_HASHTAGS.map((ht) => (
                <button
                  key={ht.tag}
                  onClick={() => toggleHashtag(ht.tag)}
                  className={cn("w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors", selectedHashtags.includes(ht.tag) ? "bg-purple/10 text-purple" : "bg-gray-50 text-gray-700 hover:bg-gray-100")}
                >
                  <div className="flex items-center gap-2">
                    <Hash className="h-3.5 w-3.5" />
                    <span className="font-medium">{ht.tag}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">{ht.relevance}%</span>
                    {selectedHashtags.includes(ht.tag) ? <X className="h-3.5 w-3.5" /> : <Plus className="h-3.5 w-3.5" />}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Best Times to Post */}
          <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-5">
            <h2 className="text-sm font-semibold text-gray-900 mb-1 flex items-center gap-2">
              <Clock className="h-4 w-4 text-emerald-500" />
              Best Times to Post
            </h2>
            <p className="text-xs text-gray-500 mb-4">Based on your audience activity</p>
            <div className="space-y-2">
              {BEST_TIMES.map((bt) => (
                <div key={bt.day} className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-50">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-900 w-24">{bt.day}</span>
                    <span className="text-xs text-gray-500">{bt.time}</span>
                  </div>
                  <span className={cn("px-2 py-0.5 text-xs rounded-full", bt.engagement === "Very High" ? "bg-green-100 text-green-700" : bt.engagement === "High" ? "bg-emerald-100 text-emerald-700" : "bg-yellow-100 text-yellow-700")}>
                    {bt.engagement}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Preview */}
          <div className="rounded-xl border border-gray-100 bg-white shadow-[var(--shadow-card)] p-5">
            <h2 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Eye className="h-4 w-4 text-blue-500" />
              Preview
            </h2>
            <div className="rounded-lg bg-gray-900 aspect-[9/16] flex items-center justify-center">
              <div className="text-center">
                <Upload className="h-8 w-8 text-gray-600 mx-auto mb-2" />
                <p className="text-xs text-gray-500">Upload content to preview</p>
              </div>
            </div>
            {caption && <p className="text-xs text-gray-600 mt-3 line-clamp-3">{caption}</p>}
          </div>
        </div>
      </div>
    </PageShell>
  );
}
