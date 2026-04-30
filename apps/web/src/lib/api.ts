const prefix = import.meta.env.VITE_API_URL ?? "";

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
