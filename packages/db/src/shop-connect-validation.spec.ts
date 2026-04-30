import { describe, expect, it } from "vitest";
import {
  formatShopConnectValidationReport,
  vaultAccessTokenBlobLooksEncrypted,
} from "./shop-connect-validation";

describe("vaultAccessTokenBlobLooksEncrypted", () => {
  it("accepts Frodo AES-GCM envelope (base64 JSON)", () => {
    const envelope = {
      ciphertext: Buffer.from("cipher-bytes").toString("base64"),
      iv: Buffer.from("iv-bytes-16b").toString("base64"),
      authTag: Buffer.from("tag16").toString("base64"),
    };
    const blob = Buffer.from(JSON.stringify(envelope), "utf8").toString(
      "base64",
    );
    const r = vaultAccessTokenBlobLooksEncrypted(blob);
    expect(r.ok).toBe(true);
  });

  it("rejects JWT-shaped plaintext", () => {
    const r = vaultAccessTokenBlobLooksEncrypted(
      "eyJhbGci.a.b",
    );
    expect(r.ok).toBe(false);
    expect(r.detail).toContain("JWT");
  });

  it("rejects random garbage", () => {
    const r = vaultAccessTokenBlobLooksEncrypted("not-base64-at-all!!!");
    expect(r.ok).toBe(false);
  });
});

describe("formatShopConnectValidationReport", () => {
  it("includes OVERALL summary line", () => {
    const text = formatShopConnectValidationReport({
      workspaceId: "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
      summary: "PASS",
      checks: [
        { name: "connected_account_shop", ok: true, detail: "ok" },
      ],
      meta: {
        connectedAccountId: "ca",
        shopCount: 0,
        shopIdsSample: [],
        latestDiscoveryJobId: null,
        latestDiscoveryJobStatus: null,
        latestDiscoveryJobItemsSynced: null,
        dedupeKeyPresent: true,
      },
    });
    expect(text).toContain("OVERALL: PASS");
    expect(text).toContain("[PASS] connected_account_shop");
  });
});
