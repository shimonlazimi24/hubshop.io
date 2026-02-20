"use client";

import { useState } from "react";
import { MessageSquare, Reply, EyeOff, Trash2, MoreHorizontal, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface AdComment {
  id: string;
  ad_name: string;
  ad_id: string;
  commenter_username: string;
  commenter_display_name: string;
  text: string;
  created_at: string;
  likes: number;
  is_hidden: boolean;
  replied: boolean;
}

const MOCK_COMMENTS: AdComment[] = [
  {
    id: "cmt-1",
    ad_name: "Spring Collection Ad",
    ad_id: "ad-101",
    commenter_username: "happy_shopper",
    commenter_display_name: "Happy Shopper",
    text: "Love this! Where can I get the blue one?",
    created_at: "2026-02-20T10:30:00Z",
    likes: 12,
    is_hidden: false,
    replied: false,
  },
  {
    id: "cmt-2",
    ad_name: "Spring Collection Ad",
    ad_id: "ad-101",
    commenter_username: "curious_buyer",
    commenter_display_name: "Curious Buyer",
    text: "How long does shipping take?",
    created_at: "2026-02-20T09:45:00Z",
    likes: 5,
    is_hidden: false,
    replied: true,
  },
  {
    id: "cmt-3",
    ad_name: "Brand Awareness Video",
    ad_id: "ad-102",
    commenter_username: "troll_account",
    commenter_display_name: "Random User",
    text: "This is a scam don't buy",
    created_at: "2026-02-20T08:15:00Z",
    likes: 0,
    is_hidden: false,
    replied: false,
  },
  {
    id: "cmt-4",
    ad_name: "Product Demo Reel",
    ad_id: "ad-103",
    commenter_username: "tech_fan_tt",
    commenter_display_name: "Tech Fan",
    text: "Great demo! Does it come in black?",
    created_at: "2026-02-19T22:30:00Z",
    likes: 8,
    is_hidden: false,
    replied: false,
  },
  {
    id: "cmt-5",
    ad_name: "Product Demo Reel",
    ad_id: "ad-103",
    commenter_username: "review_queen",
    commenter_display_name: "Review Queen",
    text: "Just ordered mine! Can't wait for it to arrive.",
    created_at: "2026-02-19T20:00:00Z",
    likes: 15,
    is_hidden: false,
    replied: true,
  },
  {
    id: "cmt-6",
    ad_name: "Flash Sale Ad",
    ad_id: "ad-104",
    commenter_username: "bargain_hunter",
    commenter_display_name: "Bargain Hunter",
    text: "Is this still available? The link doesn't work.",
    created_at: "2026-02-19T18:00:00Z",
    likes: 3,
    is_hidden: false,
    replied: false,
  },
  {
    id: "cmt-7",
    ad_name: "Brand Awareness Video",
    ad_id: "ad-102",
    commenter_username: "spam_bot_123",
    commenter_display_name: "Bot Account",
    text: "Check my profile for free stuff!!!",
    created_at: "2026-02-19T16:00:00Z",
    likes: 0,
    is_hidden: true,
    replied: false,
  },
];

export default function AdCommentsPage() {
  const [comments, setComments] = useState<AdComment[]>(MOCK_COMMENTS);
  const [filterAd, setFilterAd] = useState("");
  const [showHidden, setShowHidden] = useState(false);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);

  const adNames = [...new Set(comments.map((c) => c.ad_name))];

  const filteredComments = comments.filter((c) => {
    if (filterAd && c.ad_name !== filterAd) return false;
    if (!showHidden && c.is_hidden) return false;
    return true;
  });

  function handleHide(commentId: string) {
    setComments((prev) =>
      prev.map((c) => (c.id === commentId ? { ...c, is_hidden: !c.is_hidden } : c))
    );
    setActiveMenu(null);
  }

  function handleDelete(commentId: string) {
    setComments((prev) => prev.filter((c) => c.id !== commentId));
    setActiveMenu(null);
  }

  return (
    <div className="max-w-6xl">
      {/* Filters */}
      <div className="flex items-center gap-4 mb-4">
        <select
          value={filterAd}
          onChange={(e) => setFilterAd(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm"
        >
          <option value="">All Ads</option>
          {adNames.map((name) => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm text-gray-600">
          <input
            type="checkbox"
            checked={showHidden}
            onChange={(e) => setShowHidden(e.target.checked)}
            className="rounded border-gray-300"
          />
          Show hidden
        </label>
        <div className="flex-1" />
        <p className="text-sm text-gray-500">
          {filteredComments.length} comment{filteredComments.length !== 1 ? "s" : ""}
        </p>
      </div>

      {/* Comments List */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="divide-y divide-gray-200">
          {filteredComments.map((comment) => (
            <div
              key={comment.id}
              className={cn("px-4 py-4 hover:bg-gray-50", comment.is_hidden && "opacity-50")}
            >
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 text-sm font-medium flex-shrink-0">
                  {comment.commenter_display_name[0]}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-gray-900">
                      {comment.commenter_display_name}
                    </span>
                    <span className="text-xs text-gray-400">@{comment.commenter_username}</span>
                    <span className="text-xs text-gray-400">
                      {new Date(comment.created_at).toLocaleDateString()}
                    </span>
                    {comment.replied && (
                      <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] rounded-full bg-green-100 text-green-700">
                        <Reply className="h-2.5 w-2.5" />
                        Replied
                      </span>
                    )}
                    {comment.is_hidden && (
                      <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] rounded-full bg-gray-100 text-gray-600">
                        <EyeOff className="h-2.5 w-2.5" />
                        Hidden
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-700">{comment.text}</p>
                  <div className="flex items-center gap-4 mt-2">
                    <span className="text-xs text-gray-400">
                      on <span className="font-medium text-gray-500">{comment.ad_name}</span>
                    </span>
                    <span className="text-xs text-gray-400">{comment.likes} likes</span>
                  </div>
                </div>
                <div className="relative flex-shrink-0">
                  <button
                    onClick={() => setActiveMenu(activeMenu === comment.id ? null : comment.id)}
                    className="p-1 rounded hover:bg-gray-100 transition-colors"
                  >
                    <MoreHorizontal className="h-4 w-4 text-gray-400" />
                  </button>
                  {activeMenu === comment.id && (
                    <div className="absolute right-0 top-8 w-36 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10">
                      <button
                        onClick={() => {/* placeholder reply */; setActiveMenu(null);}}
                        className="flex items-center gap-2 w-full px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        <Reply className="h-3.5 w-3.5" />
                        Reply
                      </button>
                      <button
                        onClick={() => handleHide(comment.id)}
                        className="flex items-center gap-2 w-full px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        <EyeOff className="h-3.5 w-3.5" />
                        {comment.is_hidden ? "Unhide" : "Hide"}
                      </button>
                      <button
                        onClick={() => handleDelete(comment.id)}
                        className="flex items-center gap-2 w-full px-3 py-1.5 text-sm text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {filteredComments.length === 0 && (
            <div className="px-4 py-8 text-center text-gray-500">
              <MessageSquare className="h-8 w-8 text-gray-300 mx-auto mb-2" />
              <p className="text-sm">No comments found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
