const prefix = import.meta.env.VITE_API_URL ?? "";

/** Shown when fetch fails or Vite proxy cannot reach the API (e.g. ECONNREFUSED). */
export const API_DOWN_HINT = import.meta.env.DEV
  ? "Could not reach the API. In another terminal run: npx --yes pnpm@9.15.4 dev:api (from the frodo folder). Needs Postgres and apps/api/.env."
  : "Could not reach the server. Check your connection or try again later.";

const USER_FACING_5XX =
  "We couldn’t complete this request. Please try again in a few minutes. If it keeps happening, contact support.";

const DEV_5XX_SUFFIX =
  " — Dev: check the API process (Postgres running? DATABASE_URL set? run pnpm db:migrate).";

function isGenericServerErrorMessage(msg: string): boolean {
  const s = msg.trim().toLowerCase();
  return (
    s.length === 0 ||
    s === "internal server error" ||
    s.startsWith("internal server error")
  );
}

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

  if (res.status >= 500) {
    if (import.meta.env.DEV) {
      const detail =
        fromApi && !isGenericServerErrorMessage(fromApi)
          ? fromApi
          : text.trim() && !text.trim().startsWith("<")
            ? text.trim().slice(0, 300)
            : null;
      if (detail) {
        return `${detail}${DEV_5XX_SUFFIX}`;
      }
      return `${USER_FACING_5XX}${DEV_5XX_SUFFIX}`;
    }
    return USER_FACING_5XX;
  }

  if (fromApi) return fromApi;
  if (text.trim()) return text.trim().slice(0, 400);
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
