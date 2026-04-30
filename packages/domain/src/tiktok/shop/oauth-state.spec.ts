import { describe, expect, it } from "vitest";
import {
  ShopOAuthStateError,
  signShopOAuthState,
  verifyShopOAuthState,
} from "./oauth-state";

describe("signShopOAuthState / verifyShopOAuthState", () => {
  const secret = "test-secret-key-minimum-length";

  it("round-trips and attaches nonce + expiry", () => {
    const { token, workspaceId, userId, nonce, exp, iat } = signShopOAuthState(
      {
        workspaceId: "11111111-1111-4111-8111-111111111111",
        userId: "22222222-2222-4222-8222-222222222222",
        nowSec: 1_700_000_000,
        ttlSec: 600,
      },
      secret,
    );
    expect(workspaceId).toBe("11111111-1111-4111-8111-111111111111");
    expect(userId).toBe("22222222-2222-4222-8222-222222222222");
    expect(nonce.length).toBeGreaterThan(8);
    expect(exp - iat).toBe(600);

    const payload = verifyShopOAuthState(token, secret, {
      nowSec: 1_700_000_100,
    });
    expect(payload.workspaceId).toBe(workspaceId);
    expect(payload.userId).toBe(userId);
  });

  it("rejects tampered token", () => {
    const { token } = signShopOAuthState(
      {
        workspaceId: "11111111-1111-4111-8111-111111111111",
        userId: "22222222-2222-4222-8222-222222222222",
        nowSec: 100,
        ttlSec: 600,
      },
      secret,
    );
    const i = token.lastIndexOf(".");
    const tampered =
      i === -1 ? `${token}x` : `${token.slice(0, i + 1)}bbbb`;
    expect(() => verifyShopOAuthState(tampered, secret, { nowSec: 200 })).toThrow(
      ShopOAuthStateError,
    );
  });

  it("rejects expired state", () => {
    const { token } = signShopOAuthState(
      {
        workspaceId: "11111111-1111-4111-8111-111111111111",
        userId: "22222222-2222-4222-8222-222222222222",
        nowSec: 100,
        ttlSec: 10,
      },
      secret,
    );
    expect(() =>
      verifyShopOAuthState(token, secret, { nowSec: 200 }),
    ).toThrowError(/state_expired/);
  });
});
