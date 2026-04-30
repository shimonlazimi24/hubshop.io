import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import { and, desc, eq } from "drizzle-orm";
import * as schema from "./schema";
import {
  connectedAccounts,
  shops,
  syncJobs,
  tokenVault,
  workerDedupeKeys,
} from "./schema";

type ValidationDb = PostgresJsDatabase<typeof schema>;

export type ShopConnectValidationSummary = "PASS" | "FAIL";

export interface ShopConnectValidationCheck {
  name: string;
  ok: boolean;
  detail: string;
}

export interface ShopConnectValidationMeta {
  connectedAccountId: string | null;
  shopCount: number;
  shopIdsSample: string[];
  latestDiscoveryJobId: string | null;
  latestDiscoveryJobStatus: string | null;
  latestDiscoveryJobItemsSynced: number | null;
  dedupeKeyPresent: boolean | null;
}

export interface ShopConnectValidationResult {
  workspaceId: string;
  summary: ShopConnectValidationSummary;
  checks: ShopConnectValidationCheck[];
  meta: ShopConnectValidationMeta;
}

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

/**
 * Frodo vault stores base64(JSON.stringify({ ciphertext, iv, authTag })).
 * Returns whether the blob matches that envelope (does not prove decryption works).
 */
export function vaultAccessTokenBlobLooksEncrypted(blob: string): {
  ok: boolean;
  detail: string;
} {
  const trimmed = blob.trim();
  if (!trimmed) {
    return { ok: false, detail: "empty blob" };
  }

  // Obvious JWT-shaped plaintext (three segments, no vault JSON inside)
  if (/^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/.test(trimmed)) {
    return {
      ok: false,
      detail:
        "looks like a plaintext JWT (three dot-separated segments); expected base64 vault envelope",
    };
  }

  try {
    const json = Buffer.from(trimmed, "base64").toString("utf8");
    const o = JSON.parse(json) as Record<string, unknown>;
    const { ciphertext, iv, authTag } = o;
    if (
      typeof ciphertext !== "string" ||
      typeof iv !== "string" ||
      typeof authTag !== "string"
    ) {
      return {
        ok: false,
        detail:
          "decoded JSON missing ciphertext / iv / authTag (expected Frodo AES-GCM envelope)",
      };
    }
    if (
      !ciphertext.length ||
      !iv.length ||
      !authTag.length
    ) {
      return { ok: false, detail: "envelope fields present but empty" };
    }
    return { ok: true, detail: "matches Frodo vault envelope shape (base64 JSON)" };
  } catch {
    return {
      ok: false,
      detail: "not valid base64-encoded JSON vault envelope",
    };
  }
}

function push(
  checks: ShopConnectValidationCheck[],
  name: string,
  ok: boolean,
  detail: string,
): void {
  checks.push({ name, ok, detail });
}

export async function validateShopConnectForWorkspace(
  db: ValidationDb,
  workspaceId: string,
): Promise<ShopConnectValidationResult> {
  const checks: ShopConnectValidationCheck[] = [];

  if (!UUID_RE.test(workspaceId.trim())) {
    push(
      checks,
      "workspace_id_format",
      false,
      "workspaceId must be a UUID",
    );
    return {
      workspaceId,
      summary: "FAIL",
      checks,
      meta: {
        connectedAccountId: null,
        shopCount: 0,
        shopIdsSample: [],
        latestDiscoveryJobId: null,
        latestDiscoveryJobStatus: null,
        latestDiscoveryJobItemsSynced: null,
        dedupeKeyPresent: null,
      },
    };
  }

  const ws = workspaceId.trim();

  const [latestAccount] = await db
    .select({
      id: connectedAccounts.id,
      status: connectedAccounts.status,
      platformAccountId: connectedAccounts.platformAccountId,
      updatedAt: connectedAccounts.updatedAt,
    })
    .from(connectedAccounts)
    .where(
      and(
        eq(connectedAccounts.workspaceId, ws),
        eq(connectedAccounts.platform, "shop"),
      ),
    )
    .orderBy(desc(connectedAccounts.updatedAt))
    .limit(1);

  if (!latestAccount) {
    push(
      checks,
      "connected_account_shop",
      false,
      "no connected_accounts row for workspace with platform=shop",
    );
    return {
      workspaceId: ws,
      summary: "FAIL",
      checks,
      meta: {
        connectedAccountId: null,
        shopCount: 0,
        shopIdsSample: [],
        latestDiscoveryJobId: null,
        latestDiscoveryJobStatus: null,
        latestDiscoveryJobItemsSynced: null,
        dedupeKeyPresent: null,
      },
    };
  }

  push(
    checks,
    "connected_account_shop",
    true,
    `id=${latestAccount.id} status=${latestAccount.status} platform_account_id=${latestAccount.platformAccountId} updated_at=${latestAccount.updatedAt?.toISOString?.() ?? String(latestAccount.updatedAt)}`,
  );

  const accountOk =
    latestAccount.status === "active";
  push(
    checks,
    "connected_account_active",
    accountOk,
    accountOk
      ? "status is active"
      : `expected status=active, got ${latestAccount.status}`,
  );

  const [vaultRow] = await db
    .select({
      id: tokenVault.id,
      encryptedAccessToken: tokenVault.encryptedAccessToken,
      encryptedRefreshToken: tokenVault.encryptedRefreshToken,
    })
    .from(tokenVault)
    .where(eq(tokenVault.connectedAccountId, latestAccount.id))
    .limit(1);

  if (!vaultRow) {
    push(checks, "token_vault_row", false, "no token_vault row for connected account");
  } else {
    push(checks, "token_vault_row", true, `vault id=${vaultRow.id}`);
    const enc = vaultAccessTokenBlobLooksEncrypted(vaultRow.encryptedAccessToken);
    push(
      checks,
      "encrypted_access_token_envelope",
      enc.ok,
      enc.detail,
    );
    if (vaultRow.encryptedRefreshToken?.trim()) {
      const ref = vaultAccessTokenBlobLooksEncrypted(
        vaultRow.encryptedRefreshToken,
      );
      push(checks, "encrypted_refresh_token_envelope", ref.ok, ref.detail);
    } else {
      push(
        checks,
        "encrypted_refresh_token_envelope",
        true,
        "no refresh token stored (optional)",
      );
    }
  }

  const [latestJob] = await db
    .select({
      id: syncJobs.id,
      status: syncJobs.status,
      itemsSynced: syncJobs.itemsSynced,
      errorMessage: syncJobs.errorMessage,
      completedAt: syncJobs.completedAt,
      createdAt: syncJobs.createdAt,
    })
    .from(syncJobs)
    .where(
      and(
        eq(syncJobs.workspaceId, ws),
        eq(syncJobs.connectedAccountId, latestAccount.id),
        eq(syncJobs.syncType, "shop_discovery"),
      ),
    )
    .orderBy(desc(syncJobs.createdAt))
    .limit(1);

  if (!latestJob) {
    push(
      checks,
      "sync_job_shop_discovery",
      false,
      "no sync_jobs row with sync_type=shop_discovery for this account",
    );
  } else {
    const jobOk = latestJob.status === "completed";
    const errHint =
      latestJob.errorMessage && latestJob.status === "failed"
        ? ` error_message_prefix=${JSON.stringify(latestJob.errorMessage.slice(0, 120))}`
        : "";
    push(
      checks,
      "sync_job_shop_discovery",
      jobOk,
      jobOk
        ? `latest job id=${latestJob.id} status=${latestJob.status} items_synced=${latestJob.itemsSynced} completed_at=${latestJob.completedAt?.toISOString?.() ?? "null"}`
        : `latest job id=${latestJob.id} status=${latestJob.status}${errHint}`,
    );
  }

  const shopRows = await db
    .select({
      shopId: shops.shopId,
      discoverySnapshotJson: shops.discoverySnapshotJson,
    })
    .from(shops)
    .where(
      and(
        eq(shops.workspaceId, ws),
        eq(shops.connectedAccountId, latestAccount.id),
      ),
    );

  const withSnapshot = shopRows.filter((r) => r.discoverySnapshotJson != null);
  push(
    checks,
    "shops_rows",
    shopRows.length > 0,
    shopRows.length === 0
      ? "no shops rows for workspace + connected_account (discovery may not have run yet)"
      : `${shopRows.length} shop row(s); ${withSnapshot.length} with discovery_snapshot_json`,
  );

  const dedupeKey = `shop_discovery:${latestAccount.id}`;
  const [dedupe] = await db
    .select({ id: workerDedupeKeys.id })
    .from(workerDedupeKeys)
    .where(eq(workerDedupeKeys.dedupeKey, dedupeKey))
    .limit(1);

  push(
    checks,
    "worker_dedupe_key",
    dedupe != null,
    dedupe
      ? `dedupe key present (${dedupeKey})`
      : `missing worker_dedupe_keys row for ${dedupeKey} (job may not have been processed yet)`,
  );

  const failed = checks.filter((c) => !c.ok);
  const summary: ShopConnectValidationSummary =
    failed.length === 0 ? "PASS" : "FAIL";

  return {
    workspaceId: ws,
    summary,
    checks,
    meta: {
      connectedAccountId: latestAccount.id,
      shopCount: shopRows.length,
      shopIdsSample: shopRows.slice(0, 8).map((r) => r.shopId),
      latestDiscoveryJobId: latestJob?.id ?? null,
      latestDiscoveryJobStatus: latestJob?.status ?? null,
      latestDiscoveryJobItemsSynced: latestJob?.itemsSynced ?? null,
      dedupeKeyPresent: dedupe != null,
    },
  };
}

/** Plain-text report for CLI / logs */
export function formatShopConnectValidationReport(
  result: ShopConnectValidationResult,
): string {
  const lines: string[] = [
    "=== TikTok Shop Connect — staging validation ===",
    `Workspace: ${result.workspaceId}`,
    "",
  ];

  for (const c of result.checks) {
    const mark = c.ok ? "PASS" : "FAIL";
    lines.push(`[${mark}] ${c.name}`);
    lines.push(`       ${c.detail}`);
    lines.push("");
  }

  lines.push("--- Summary ---");
  lines.push(`(meta) connected_account_id=${result.meta.connectedAccountId ?? "null"}`);
  lines.push(`(meta) shops=${result.meta.shopCount} sample_shop_ids=${result.meta.shopIdsSample.join(", ") || "(none)"}`);
  lines.push(
    `(meta) latest_shop_discovery_job=${result.meta.latestDiscoveryJobStatus ?? "none"} items_synced=${result.meta.latestDiscoveryJobItemsSynced ?? "n/a"} dedupe=${result.meta.dedupeKeyPresent}`,
  );
  lines.push("");
  lines.push(`OVERALL: ${result.summary}`);
  return lines.join("\n");
}
