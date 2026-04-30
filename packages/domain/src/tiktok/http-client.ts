export interface RetryPolicy {
  maxAttempts: number;
  baseDelayMs: number;
}

const DEFAULT_RETRY: RetryPolicy = {
  maxAttempts: 3,
  baseDelayMs: 1000,
};

/** Minimal fetch wrapper with exponential backoff for 429/5xx. */
export async function fetchWithRetry(
  input: string,
  init?: RequestInit,
  policy: RetryPolicy = DEFAULT_RETRY,
  fetchImpl: typeof fetch = fetch,
): Promise<Response> {
  let attempt = 0;
  let delay = policy.baseDelayMs;
  while (attempt < policy.maxAttempts) {
    const res = await fetchImpl(input, init);
    if (res.status !== 429 && res.status < 500) {
      return res;
    }
    attempt += 1;
    if (attempt >= policy.maxAttempts) {
      return res;
    }
    await new Promise((r) => setTimeout(r, delay));
    delay *= 2;
  }
  throw new Error("fetchWithRetry: unreachable");
}
