/**
 * Apply Drizzle SQL from packages/db/migrations (bundled under dist/migrations after build).
 * Uses DATABASE_MIGRATION_URL when set, otherwise DATABASE_URL.
 */
import fs from "node:fs";
import path from "node:path";
import { drizzle } from "drizzle-orm/postgres-js";
import { migrate } from "drizzle-orm/postgres-js/migrator";
import postgres from "postgres";
import { resolveMigrationDatabaseUrl } from "./migration-url";

/** Project-specific key; must not collide with other advisory lock users in the same DB. */
const ADVISORY_LOCK_KEY = 582947103618;

function resolveMigrationsFolder(): string {
  const nextToDist = path.join(__dirname, "migrations");
  if (fs.existsSync(path.join(nextToDist, "meta", "_journal.json"))) {
    return nextToDist;
  }
  return path.join(__dirname, "..", "migrations");
}

export type RunDrizzleMigrationsOptions = {
  /** When true (default), serializes concurrent runs across API replicas. CLI migrate uses false. */
  useAdvisoryLock?: boolean;
  env?: NodeJS.ProcessEnv;
};

export async function runDrizzleMigrationsFromEnv(
  options: RunDrizzleMigrationsOptions = {},
): Promise<void> {
  const env = options.env ?? process.env;
  const useAdvisoryLock = options.useAdvisoryLock !== false;

  const resolved = resolveMigrationDatabaseUrl(env);
  if (!resolved) {
    throw new Error(
      "Set DATABASE_MIGRATION_URL or DATABASE_URL to run Drizzle migrations (see docs/v2/ENVIRONMENT.md).",
    );
  }

  const migrationsFolder = resolveMigrationsFolder();
  if (!fs.existsSync(path.join(migrationsFolder, "meta", "_journal.json"))) {
    throw new Error(
      `Drizzle migrations folder missing or incomplete: ${migrationsFolder} (expected meta/_journal.json).`,
    );
  }

  const client = postgres(resolved, { max: 1 });
  try {
    if (useAdvisoryLock) {
      await client.unsafe(`SELECT pg_advisory_lock(${ADVISORY_LOCK_KEY})`);
    }
    const db = drizzle(client);
    await migrate(db, { migrationsFolder });
    console.log("Migrations complete.");
  } finally {
    if (useAdvisoryLock) {
      try {
        await client.unsafe(`SELECT pg_advisory_unlock(${ADVISORY_LOCK_KEY})`);
      } catch {
        /* ignore unlock errors */
      }
    }
    await client.end({ timeout: 5 });
  }
}
