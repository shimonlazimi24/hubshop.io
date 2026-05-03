import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

export type FrodoDb = ReturnType<typeof createDb>;

export function createDb(connectionString: string) {
  const client = postgres(connectionString, { max: 10 });
  return drizzle(client, { schema });
}

export { schema };
export { runDrizzleMigrationsFromEnv } from "./run-migrations";
export * from "./schema";
export * from "./shop-connect-validation";
export * from "./shop-commerce-validation";
