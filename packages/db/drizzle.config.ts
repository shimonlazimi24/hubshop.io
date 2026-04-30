import { defineConfig } from "drizzle-kit";

const migrationUrl =
  process.env.DATABASE_MIGRATION_URL?.trim() ||
  process.env.DATABASE_URL?.trim();
if (!migrationUrl) {
  throw new Error(
    "Drizzle Kit requires DATABASE_MIGRATION_URL or DATABASE_URL (see docs/v2/ENVIRONMENT.md).",
  );
}

export default defineConfig({
  schema: "./src/schema/index.ts",
  out: "./migrations",
  dialect: "postgresql",
  dbCredentials: {
    url: migrationUrl,
  },
});
