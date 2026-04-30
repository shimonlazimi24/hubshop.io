/**
 * Apply Drizzle migrations from packages/db/migrations.
 * Uses DATABASE_MIGRATION_URL when set, otherwise DATABASE_URL.
 * Run after legacy Alembic migrations created core tables.
 */
import path from "node:path";
import { drizzle } from "drizzle-orm/postgres-js";
import { migrate } from "drizzle-orm/postgres-js/migrator";
import postgres from "postgres";
import { resolveMigrationDatabaseUrl } from "./migration-url";

async function main(): Promise<void> {
  const resolved = resolveMigrationDatabaseUrl(process.env);
  if (!resolved) {
    console.error(
      "Set DATABASE_MIGRATION_URL or DATABASE_URL to run Drizzle migrations (see docs/v2/ENVIRONMENT.md).",
    );
    process.exit(1);
  }

  const client = postgres(resolved, { max: 1 });
  const db = drizzle(client);

  const migrationsFolder = path.join(__dirname, "..", "migrations");

  await migrate(db, { migrationsFolder });
  await client.end();
  console.log("Migrations complete.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
