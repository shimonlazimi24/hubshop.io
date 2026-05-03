const prefix = import.meta.env.VITE_API_URL ?? "";

/** Shown when fetch fails or Vite proxy cannot reach the API (e.g. ECONNREFUSED). */
export const API_DOWN_HINT =
  "Could not reach the API. In another terminal run: npx --yes pnpm@9.15.4 dev:api (from the frodo folder). Needs Postgres and apps/api/.env.";

/** Response reached the API but the server failed (5xx) — check API logs / DB / migrations. */
export const API_SERVER_ERROR_HINT =
  "The API returned a server error (HTTP 5xx). Check the terminal running dev:api: Postgres reachable? DATABASE_URL correct? Did you run pnpm db:migrate?";

export function formatApiErr(body: unknown): string | undefined {
  if (!body || typeof body !== "object") return undefined;
  const msg = (body as { message?: unknown }).message;
  if (typeof msg === "string") return msg;
  if (Array.isArray(msg)) {
    const parts = msg.filter((x): x is string => typeof x === "string");
    if (parts.length) return parts.join("; ");
  }
  return undefined;
}

/** Reads body once; prefers Nest `message`, then non-JSON snippet, then status-based hints. */
export async function errorMessageFromFailedResponse(
  res: Response,
): Promise<string> {
  const text = await res.text();
  let body: unknown = null;
  if (text.trim()) {
    try {
      body = JSON.parse(text) as unknown;
    } catch {
      /* HTML or plain text error page */
    }
  }
  const fromApi = formatApiErr(body);
  if (fromApi) return fromApi;
  if (text.trim()) return text.trim().slice(0, 400);
  if (res.status >= 500) {
    return `${API_SERVER_ERROR_HINT} (HTTP ${res.status})`;
  }
  return `HTTP ${res.status}`;
}

export function getApiPrefix(): string {
  return prefix;
}

export function authHeaders(workspaceId?: string | null): HeadersInit {
  const h: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const token = localStorage.getItem("frodo_access_token");
  if (token) {
    h.Authorization = `Bearer ${token}`;
  }
  const ws =
    workspaceId ?? localStorage.getItem("frodo_workspace_id") ?? undefined;
  if (ws) {
    h["X-Workspace-Id"] = ws;
  }
  return h;
}
