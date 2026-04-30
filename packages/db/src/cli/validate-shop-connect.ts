/**
 * CLI: validate TikTok Shop Connect slice for a workspace (Postgres).
 *
 * Usage:
 *   DATABASE_URL=... pnpm --filter @frodo/db validate:shop-connect -- --workspace <uuid>
 *
 * Uses DATABASE_URL, or DATABASE_MIGRATION_URL if DATABASE_URL is unset.
 */
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "../schema";
import { resolveDatabaseCheckUrl } from "../migration-url";
import {
  formatShopConnectValidationReport,
  validateShopConnectForWorkspace,
} from "../shop-connect-validation";

function parseWorkspaceArg(): string | null {
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === "--workspace" && argv[i + 1]) {
      return argv[i + 1];
    }
    if (a.startsWith("--workspace=")) {
      return a.slice("--workspace=".length);
    }
  }
  if (argv.length >= 1 && !argv[0].startsWith("-")) {
    return argv[0];
  }
  return null;
}

async function main(): Promise<void> {
  const workspaceId = parseWorkspaceArg();
  const databaseUrl = resolveDatabaseCheckUrl(process.env);

  if (!databaseUrl) {
    console.error(
      "DATABASE_URL or DATABASE_MIGRATION_URL is required (prefer DATABASE_URL).",
    );
    process.exit(2);
  }
  if (!workspaceId?.trim()) {
    console.error(
      "Usage: validate:shop-connect -- --workspace <uuid>\n   or: validate:shop-connect -- <uuid>",
    );
    process.exit(2);
  }

  const client = postgres(databaseUrl, { max: 1 });
  const db = drizzle(client, { schema });

  try {
    const result = await validateShopConnectForWorkspace(db, workspaceId.trim());
    console.log(formatShopConnectValidationReport(result));
    process.exit(result.summary === "PASS" ? 0 : 1);
  } finally {
    await client.end({ timeout: 5 });
  }
}

main().catch((e) => {
  console.error(e instanceof Error ? e.message : String(e));
  process.exit(2);
});
