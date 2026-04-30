/**
 * Validate Shop products/orders sync slice for a workspace + shop (Postgres).
 *
 * Usage:
 *   DATABASE_URL=... pnpm --filter @frodo/db validate:shop-commerce -- --workspace <uuid> --shop <shops.id uuid>
 *
 * Uses DATABASE_URL, or DATABASE_MIGRATION_URL if DATABASE_URL is unset.
 */
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "../schema";
import { resolveDatabaseCheckUrl } from "../migration-url";
import {
  formatShopCommerceValidationReport,
  validateShopCommerceForWorkspace,
} from "../shop-commerce-validation";

function parseArgs(): { workspaceId: string | null; shopId: string | null } {
  const argv = process.argv.slice(2);
  let workspaceId: string | null = null;
  let shopId: string | null = null;
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === "--workspace" && argv[i + 1]) {
      workspaceId = argv[i + 1];
      i += 1;
      continue;
    }
    if (a.startsWith("--workspace=")) {
      workspaceId = a.slice("--workspace=".length);
      continue;
    }
    if (a === "--shop" && argv[i + 1]) {
      shopId = argv[i + 1];
      i += 1;
      continue;
    }
    if (a.startsWith("--shop=")) {
      shopId = a.slice("--shop=".length);
      continue;
    }
  }
  return { workspaceId, shopId };
}

async function main(): Promise<void> {
  const { workspaceId, shopId } = parseArgs();
  const databaseUrl = resolveDatabaseCheckUrl(process.env);

  if (!databaseUrl) {
    console.error(
      "DATABASE_URL or DATABASE_MIGRATION_URL is required (prefer DATABASE_URL).",
    );
    process.exit(2);
  }
  if (!workspaceId?.trim() || !shopId?.trim()) {
    console.error(
      "Usage: validate:shop-commerce -- --workspace <uuid> --shop <shops.id uuid>",
    );
    process.exit(2);
  }

  const client = postgres(databaseUrl, { max: 1 });
  const db = drizzle(client, { schema });

  try {
    const result = await validateShopCommerceForWorkspace(
      db,
      workspaceId.trim(),
      shopId.trim(),
    );
    console.log(formatShopCommerceValidationReport(result));
    process.exit(result.summary === "PASS" ? 0 : 1);
  } finally {
    await client.end({ timeout: 5 });
  }
}

main().catch((e) => {
  console.error(e instanceof Error ? e.message : String(e));
  process.exit(2);
});
