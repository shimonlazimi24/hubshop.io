import { createCipheriv, createDecipheriv, randomBytes, scryptSync } from "node:crypto";

const IV_LENGTH = 16;
const ALGO = "aes-256-gcm";

/** Derive a 32-byte key from env secret (compat with dev-only simple scheme). */
function deriveKey(secret: string): Buffer {
  return scryptSync(secret, "frodo-token-vault", 32);
}

export interface EncryptedPayload {
  ciphertext: string;
  iv: string;
  authTag: string;
}

export function encryptSecret(plainText: string, masterSecret: string): string {
  const key = deriveKey(masterSecret);
  const iv = randomBytes(IV_LENGTH);
  const cipher = createCipheriv(ALGO, key, iv);
  const encrypted = Buffer.concat([
    cipher.update(plainText, "utf8"),
    cipher.final(),
  ]);
  const tag = cipher.getAuthTag();
  const payload: EncryptedPayload = {
    ciphertext: encrypted.toString("base64"),
    iv: iv.toString("base64"),
    authTag: tag.toString("base64"),
  };
  return Buffer.from(JSON.stringify(payload), "utf8").toString("base64");
}

export function decryptSecret(blob: string, masterSecret: string): string {
  const key = deriveKey(masterSecret);
  const parsed = JSON.parse(
    Buffer.from(blob, "base64").toString("utf8"),
  ) as EncryptedPayload;
  const iv = Buffer.from(parsed.iv, "base64");
  const tag = Buffer.from(parsed.authTag, "base64");
  const ciphertext = Buffer.from(parsed.ciphertext, "base64");
  const decipher = createDecipheriv(ALGO, key, iv);
  decipher.setAuthTag(tag);
  const plain = Buffer.concat([
    decipher.update(ciphertext),
    decipher.final(),
  ]);
  return plain.toString("utf8");
}
