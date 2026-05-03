/**
 * CLI: `pnpm --filter @frodo/db migrate` / `pnpm db:migrate`.
 * Uses DATABASE_MIGRATION_URL when set, otherwise DATABASE_URL.
 * Baseline migration creates the full v2 schema (greenfield Postgres).
 */
import { runDrizzleMigrationsFromEnv } from "./run-migrations";

void runDrizzleMigrationsFromEnv({ useAdvisoryLock: false }).catch((err) => {
  console.error(err);
  process.exit(1);
});
