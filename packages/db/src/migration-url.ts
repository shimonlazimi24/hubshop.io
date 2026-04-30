/**
 * Drizzle CLI and `pnpm db:migrate` use DATABASE_MIGRATION_URL when set,
 * otherwise DATABASE_URL. API/worker must use DATABASE_URL only at runtime.
 */
export function resolveMigrationDatabaseUrl(
  env: NodeJS.ProcessEnv = process.env,
): string | undefined {
  const migration = env.DATABASE_MIGRATION_URL?.trim();
  const runtime = env.DATABASE_URL?.trim();
  return migration || runtime || undefined;
}

/** `db:check` prefers runtime URL, then migration URL (never prints the value). */
export function resolveDatabaseCheckUrl(
  env: NodeJS.ProcessEnv = process.env,
): string | undefined {
  const runtime = env.DATABASE_URL?.trim();
  const migration = env.DATABASE_MIGRATION_URL?.trim();
  return runtime || migration || undefined;
}
