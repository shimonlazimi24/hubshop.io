/**
 * Read-only row-count parity smoke test against a Postgres clone.
 * Usage: DATABASE_URL=... node packages/db/dist/parity-check.js
 * Uses DATABASE_URL, or DATABASE_MIGRATION_URL if DATABASE_URL is unset.
 */
import postgres from "postgres";
import { resolveDatabaseCheckUrl } from "./migration-url";

const tables = [
  "users",
  "organizations",
  "workspaces",
  "memberships",
  "webhook_events",
  "connected_accounts",
  "token_vault",
  "shops",
  "products",
  "orders",
] as const;

async function main(): Promise<void> {
  const url = resolveDatabaseCheckUrl(process.env);
  if (!url) {
    console.error(
      "DATABASE_URL or DATABASE_MIGRATION_URL is required (prefer DATABASE_URL).",
    );
    process.exit(1);
  }

  const sql = postgres(url, { max: 1 });

  for (const t of tables) {
    if (!/^[a-z_]+$/.test(t)) {
      throw new Error(`Invalid table name: ${t}`);
    }
    const rows = await sql.unsafe<{ c: bigint }[]>(
      `select count(*)::bigint as c from "${t}"`,
    );
    const row = rows[0];
    console.log(`${t}: ${row?.c?.toString() ?? "0"}`);
  }

  await sql.end();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
