const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface FetchOptions extends RequestInit {
  token?: string;
}

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { token, headers: customHeaders, ...rest } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((customHeaders as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    headers,
    ...rest,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Auth
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export function register(data: {
  email: string;
  password: string;
  full_name: string;
  organization_name: string;
}): Promise<TokenResponse> {
  return apiFetch("/auth/register", { method: "POST", body: JSON.stringify(data) });
}

export function login(data: { email: string; password: string }): Promise<TokenResponse> {
  return apiFetch("/auth/login", { method: "POST", body: JSON.stringify(data) });
}

export function refreshTokens(refresh_token: string): Promise<TokenResponse> {
  return apiFetch("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token }),
  });
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
}

export function getMe(token: string): Promise<UserResponse> {
  return apiFetch("/auth/me", { token });
}

// Connect
export interface ConnectedAccount {
  id: string;
  platform: string;
  platform_account_id: string;
  platform_account_name: string | null;
  status: string;
  identity_group_id: string | null;
}

export function getAuthorizeUrl(
  platform: string,
  workspaceId: string,
  token: string
): Promise<{ authorize_url: string }> {
  return apiFetch(`/connect/${platform}/authorize?workspace_id=${workspaceId}`, { token });
}

export function listConnectedAccounts(
  workspaceId: string,
  token: string
): Promise<ConnectedAccount[]> {
  return apiFetch(`/connect/accounts?workspace_id=${workspaceId}`, { token });
}
