"use client";

import { useEffect, useState } from "react";
import {
  publishVideo,
  listPublishJobs,
  getCreatorInfo,
  type PublishJob,
  type CreatorInfo,
  type PaginatedResponse,
} from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

const STATUS_COLORS: Record<string, string> = {
  PENDING: "bg-yellow-100 text-yellow-800",
  PROCESSING: "bg-blue-100 text-blue-800",
  PUBLISHED: "bg-green-100 text-green-800",
  FAILED: "bg-red-100 text-red-800",
};

export default function PublishPage() {
  const [creatorInfo, setCreatorInfo] = useState<CreatorInfo | null>(null);
  const [jobs, setJobs] = useState<PaginatedResponse<PublishJob> | null>(null);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");
  const [title, setTitle] = useState("");
  const [privacyLevel, setPrivacyLevel] = useState("PUBLIC_TO_EVERYONE");

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    Promise.all([
      getCreatorInfo(WORKSPACE_ID, token).catch(() => null),
      listPublishJobs(WORKSPACE_ID, token).catch(() => null),
    ])
      .then(([info, jobsData]) => {
        setCreatorInfo(info);
        setJobs(jobsData);
      })
      .finally(() => setLoading(false));
  }, []);

  async function handlePublish() {
    if (!token || !videoUrl) return;
    setPublishing(true);
    try {
      await publishVideo(WORKSPACE_ID, { video_url: videoUrl, title: title || undefined, privacy_level: privacyLevel }, token);
      setVideoUrl("");
      setTitle("");
      const jobsData = await listPublishJobs(WORKSPACE_ID, token);
      setJobs(jobsData);
    } catch (err) {
      console.error(err);
    } finally {
      setPublishing(false);
    }
  }

  return (
    <div className="max-w-4xl">
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h3 className="text-sm font-medium text-gray-900 mb-4">Publish New Video</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Video URL</label>
            <input
              type="url"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="https://example.com/video.mp4"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Title (optional)</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Video title"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Privacy</label>
            <select
              value={privacyLevel}
              onChange={(e) => setPrivacyLevel(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              {(creatorInfo?.privacy_level_options.length
                ? creatorInfo.privacy_level_options
                : ["PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "SELF_ONLY"]
              ).map((opt) => (
                <option key={opt} value={opt}>{opt.replace(/_/g, " ")}</option>
              ))}
            </select>
          </div>
          <button
            onClick={handlePublish}
            disabled={publishing || !videoUrl}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {publishing ? "Publishing..." : "Publish Video"}
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Recent Publish Jobs</h3>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Title</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Privacy</th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {jobs?.items.map((job) => (
              <tr key={job.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-900">{job.title || "Untitled"}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${STATUS_COLORS[job.status] || "bg-gray-100 text-gray-800"}`}>
                    {job.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">{job.privacy_level.replace(/_/g, " ")}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(job.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
            {!loading && (!jobs || jobs.items.length === 0) && (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-gray-500">No publish jobs yet</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
