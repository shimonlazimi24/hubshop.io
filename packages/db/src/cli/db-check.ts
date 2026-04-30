/**
 * Read-only Postgres connectivity and schema smoke check.
 * Does not print passwords or full connection strings.
 */
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import postgres from "postgres";
import { resolveDatabaseCheckUrl } from "../migration-url";

const CORE_V2_TABLES = [
  "users",
  "organizations",
  "workspaces",
  "memberships",
  "webhook_events",
  "connected_accounts",
  "token_vault",
  "sync_jobs",
  "shops",
  "worker_dedupe_keys",
  "products",
  "orders",
  "scheduled_job_runs",
  "feature_flags",
] as const;

function safeTargetSummary(connectionUrl: string): string {
  try {
    const normalized = connectionUrl.replace(/^postgresql\+[^:]+:/i, "postgresql:");
    const u = new URL(normalized);
    const host = u.hostname || "?";
    const port = u.port || (u.protocol === "postgresql:" ? "5432" : "");
    const database = (u.pathname || "/").replace(/^\//, "") || "?";
    return `host=${host} port=${port || "default"} database=${database}`;
  } catch {
    return "host=(unparsed) database=(unparsed)";
  }
}

function readLatestJournalTag(): string | null {
  try {
    const journalPath = join(
      __dirname,
      "..",
      "..",
      "migrations",
      "meta",
      "_journal.json",
    );
    if (!existsSync(journalPath)) {
      return null;
    }
    const raw = readFileSync(journalPath, "utf8");
    const parsed = JSON.parse(raw) as {
      entries?: Array<{ tag?: string }>;
    };
    const entries = parsed.entries ?? [];
    const last = entries[entries.length - 1];
    return last?.tag ?? null;
  } catch {
    return null;
  }
}

async function main(): Promise<void> {
  const url = resolveDatabaseCheckUrl(process.env);
  if (!url) {
    console.error(
      "DATABASE_URL or DATABASE_MIGRATION_URL is required for db:check (prefer DATABASE_URL to match API/worker runtime).",
    );
    process.exit(2);
  }

  console.log(`Connection target (redacted): ${safeTargetSummary(url)}`);

  const sql = postgres(url, { max: 1 });

  try {
    const [dbRow] = await sql<{ current_database: string }[]>`
      select current_database()::text as current_database
    `;
    const [userRow] = await sql<{ current_user: string }[]>`
      select current_user::text as current_user
    `;
    const [verRow] = await sql<{ version: string }[]>`
      select version()::text as version
    `;

    console.log(`current_database: ${dbRow?.current_database ?? "?"}`);
    console.log(`current_user: ${userRow?.current_user ?? "?"}`);
    const ver = verRow?.version ?? "?";
    console.log(`server_version: ${ver.split("\n")[0] ?? ver}`);

    console.log("core_v2_tables:");
    for (const t of CORE_V2_TABLES) {
      const [{ exists }] = await sql<{ exists: boolean }[]>`
        select exists (
          select 1
          from information_schema.tables
          where table_schema = 'public'
            and table_name = ${t}
        ) as exists
      `;
      console.log(`  ${t}: ${exists ? "yes" : "no"}`);
    }

    const [{ reg }] = await sql<{ reg: string | null }[]>`
      select to_regclass('public.__drizzle_migrations')::text as reg
    `;

    if (reg) {
      try {
        const rows = await sql.unsafe<Record<string, unknown>[]>(
          "select * from __drizzle_migrations order by created_at desc limit 3",
        );
        const latest = rows[0];
        if (latest) {
          const summary = Object.entries(latest)
            .map(([k, v]) => `${k}=${String(v)}`)
            .join(" ");
          console.log(`latest_applied_migration: ${summary}`);
        } else {
          console.log("latest_applied_migration: (table empty)");
        }
      } catch (e) {
        console.log(
          `latest_applied_migration: (could not read __drizzle_migrations: ${e instanceof Error ? e.message : String(e)})`,
        );
      }
    } else {
      const journalTag = readLatestJournalTag();
      console.log(
        journalTag
          ? `latest_applied_migration: __drizzle_migrations not present yet (repo journal latest tag: ${journalTag}; run pnpm db:migrate)`
          : "latest_applied_migration: __drizzle_migrations not present (run pnpm db:migrate)",
      );
    }

    console.log("db:check ok.");
  } finally {
    await sql.end({ timeout: 5 });
  }
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
