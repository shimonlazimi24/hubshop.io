import { describe, expect, it } from "vitest";
import { encryptSecret } from "./token-vault";

describe("token vault ciphertext", () => {
  it("does not embed plaintext access token in stored blob", () => {
    const secret =
      "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
    const token =
      "TT_ACCESS_TOKEN_PLAINTEXT_DO_NOT_LOG_abc123xyz9876543210";
    const blob = encryptSecret(token, secret);
    expect(blob).not.toContain("TT_ACCESS_TOKEN_PLAINTEXT");
    expect(blob).not.toContain("abc123xyz9876543210");
    expect(blob.length).toBeGreaterThan(32);
  });
});
