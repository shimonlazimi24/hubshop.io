CREATE TABLE IF NOT EXISTS "worker_dedupe_keys" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"dedupe_key" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "worker_dedupe_keys_dedupe_key_unique" UNIQUE("dedupe_key")
);
