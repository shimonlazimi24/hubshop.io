/** Stable Frodo / TikTok Shop slice error codes for logs and OAuth redirects. */
export const FRODO_TIKTOK_STATE_INVALID = "tiktok_state_invalid" as const;
export const FRODO_TIKTOK_TOKEN_EXCHANGE_FAILED =
  "tiktok_token_exchange_failed" as const;
export const FRODO_TIKTOK_TOKEN_MISSING_SELLER_IDENTITY =
  "tiktok_token_missing_seller_identity" as const;
export const FRODO_TIKTOK_SHOP_DISCOVERY_FAILED =
  "tiktok_shop_discovery_failed" as const;
export const FRODO_SQS_ENQUEUE_FAILED = "sqs_enqueue_failed" as const;
export const FRODO_VAULT_DECRYPT_FAILED = "vault_decrypt_failed" as const;

export type FrodoTiktokShopErrorCode =
  | typeof FRODO_TIKTOK_STATE_INVALID
  | typeof FRODO_TIKTOK_TOKEN_EXCHANGE_FAILED
  | typeof FRODO_TIKTOK_TOKEN_MISSING_SELLER_IDENTITY
  | typeof FRODO_TIKTOK_SHOP_DISCOVERY_FAILED
  | typeof FRODO_SQS_ENQUEUE_FAILED
  | typeof FRODO_VAULT_DECRYPT_FAILED;
