import { describe, expect, it, vi } from "vitest";
import { fetchWithRetry } from "./http-client";

describe("fetchWithRetry", () => {
  it("returns non-retry responses immediately", async () => {
    const ok = new Response(null, { status: 200 });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok));
    const res = await fetchWithRetry("https://example.com/api");
    expect(res.status).toBe(200);
  });
});
