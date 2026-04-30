import { pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core";

/** Worker-level idempotency for commerce/sync envelope dedupe keys (additive migration). */
export const workerDedupeKeys = pgTable("worker_dedupe_keys", {
  id: uuid("id").defaultRandom().primaryKey(),
  dedupeKey: text("dedupe_key").notNull().unique(),
  createdAt: timestamp("created_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
});
