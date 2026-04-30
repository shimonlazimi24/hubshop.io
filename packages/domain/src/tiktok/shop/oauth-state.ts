import { createHmac, randomBytes, timingSafeEqual } from "node:crypto";

export interface ShopOAuthStatePayload {
  workspaceId: string;
  userId: string;
  nonce: string;
  /** Unix seconds */
  iat: number;
  /** Unix seconds */
  exp: number;
}

const MAX_STATE_AGE_SEC = 900;

function b64urlEncode(buf: Buffer): string {
  return buf
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

function b64urlDecode(s: string): Buffer {
  const pad = 4 - (s.length % 4 || 4);
  const b64 = (s + "=".repeat(pad)).replace(/-/g, "+").replace(/_/g, "/");
  return Buffer.from(b64, "base64");
}

/** Signed opaque state for TikTok Shop OAuth (HMAC-SHA256 over base64url JSON). */
export function signShopOAuthState(
  payload: Omit<ShopOAuthStatePayload, "nonce" | "iat" | "exp"> & {
    nonce?: string;
    nowSec?: number;
    ttlSec?: number;
  },
  secret: string,
): ShopOAuthStatePayload & { token: string } {
  const nowSec = payload.nowSec ?? Math.floor(Date.now() / 1000);
  const ttlSec = payload.ttlSec ?? MAX_STATE_AGE_SEC;
  const full: ShopOAuthStatePayload = {
    workspaceId: payload.workspaceId,
    userId: payload.userId,
    nonce: payload.nonce ?? randomBytes(16).toString("hex"),
    iat: nowSec,
    exp: nowSec + ttlSec,
  };
  const body = b64urlEncode(Buffer.from(JSON.stringify(full), "utf8"));
  const sig = createHmac("sha256", secret).update(body).digest();
  const sigStr = b64urlEncode(sig);
  return { ...full, token: `${body}.${sigStr}` };
}

export class ShopOAuthStateError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ShopOAuthStateError";
  }
}

export function verifyShopOAuthState(
  token: string,
  secret: string,
  options?: { nowSec?: number },
): ShopOAuthStatePayload {
  const parts = token.split(".");
  if (parts.length !== 2 || !parts[0] || !parts[1]) {
    throw new ShopOAuthStateError("invalid_state_format");
  }
  const [body, sigStr] = parts;
  const expectedSig = createHmac("sha256", secret).update(body).digest();
  let providedSig: Buffer;
  try {
    providedSig = b64urlDecode(sigStr);
  } catch {
    throw new ShopOAuthStateError("invalid_state_signature_encoding");
  }
  if (
    expectedSig.length !== providedSig.length ||
    !timingSafeEqual(expectedSig, providedSig)
  ) {
    throw new ShopOAuthStateError("invalid_state_signature");
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(b64urlDecode(body).toString("utf8"));
  } catch {
    throw new ShopOAuthStateError("invalid_state_payload");
  }
  if (
    typeof parsed !== "object" ||
    parsed === null ||
    typeof (parsed as ShopOAuthStatePayload).workspaceId !== "string" ||
    typeof (parsed as ShopOAuthStatePayload).userId !== "string" ||
    typeof (parsed as ShopOAuthStatePayload).nonce !== "string" ||
    typeof (parsed as ShopOAuthStatePayload).iat !== "number" ||
    typeof (parsed as ShopOAuthStatePayload).exp !== "number"
  ) {
    throw new ShopOAuthStateError("invalid_state_claims");
  }
  const nowSec = options?.nowSec ?? Math.floor(Date.now() / 1000);
  if (nowSec > (parsed as ShopOAuthStatePayload).exp) {
    throw new ShopOAuthStateError("state_expired");
  }
  return parsed as ShopOAuthStatePayload;
}
