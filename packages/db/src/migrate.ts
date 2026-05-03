/**
 * CLI: `pnpm --filter @frodo/db migrate` / `pnpm db:migrate`.
 * Uses DATABASE_MIGRATION_URL when set, otherwise DATABASE_URL.
 */
import { runDrizzleMigrationsFromEnv } from "./run-migrations";

void runDrizzleMigrationsFromEnv({ useAdvisoryLock: false }).catch((err) => {
  console.error(err);
  process.exit(1);
});
