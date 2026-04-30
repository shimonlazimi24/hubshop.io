import { getApiPrefix } from "./api";

export type LegacyUser = {
  id: string;
  full_name: string;
  email: string;
};

const PROFILE_EMAIL = "frodo_profile_email";
const PROFILE_NAME = "frodo_profile_name";

export function persistProfile(fullName: string, email: string) {
  localStorage.setItem(PROFILE_NAME, fullName.trim() || "User");
  localStorage.setItem(PROFILE_EMAIL, email.trim());
}

export function clearProfile() {
  localStorage.removeItem(PROFILE_NAME);
  localStorage.removeItem(PROFILE_EMAIL);
}

export function loadStoredProfile(): Pick<LegacyUser, "full_name" | "email"> {
  return {
    full_name: localStorage.getItem(PROFILE_NAME) ?? "User",
    email: localStorage.getItem(PROFILE_EMAIL) ?? "",
  };
}

export async function fetchLegacyUser(token: string): Promise<LegacyUser | null> {
  const r = await fetch(`${getApiPrefix()}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) return null;
  const j = (await r.json()) as {
    id: string;
    claims?: Record<string, unknown>;
  };
  const stored = loadStoredProfile();
  const claimsEmail =
    typeof j.claims?.email === "string" ? j.claims.email : undefined;
  const claimsName =
    typeof j.claims?.name === "string"
      ? j.claims.name
      : typeof j.claims?.full_name === "string"
        ? (j.claims.full_name as string)
        : undefined;
  return {
    id: j.id,
    full_name: claimsName ?? stored.full_name,
    email: claimsEmail ?? stored.email,
  };
}
