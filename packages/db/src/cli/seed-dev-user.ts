/**
 * Insert a fixed local user + org + default workspace (same shape as POST /api/auth/register).
 *
 * Usage (from repo root, after migrations):
 *   export DATABASE_URL='postgresql://…'
 *   pnpm db:seed:dev
 *
 * Login in the SPA:
 *   Email: dev@frodo.local
 *   Password: DevPass123
 *
 * Safe to re-run: skips if the email already exists.
 */
import { randomBytes } from "node:crypto";
import bcrypt from "bcrypt";
import { drizzle } from "drizzle-orm/postgres-js";
import { eq } from "drizzle-orm";
import postgres from "postgres";
import {
  memberships,
  organizations,
  users,
  workspaces,
} from "../schema/tables";
import * as schema from "../schema";

const DEV_EMAIL = "dev@frodo.local";
const DEV_PASSWORD = "DevPass123";
const DEV_FULL_NAME = "Dev User";
const DEV_ORG_NAME = "Dev Org";

function slugifyOrg(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "")
    .slice(0, 50);
}

async function main(): Promise<void> {
  const url = process.env.DATABASE_URL?.trim();
  if (!url) {
    console.error(
      "Set DATABASE_URL (same as apps/api/.env) to seed the dev user.",
    );
    process.exit(1);
  }

  const client = postgres(url, { max: 1 });
  const db = drizzle(client, { schema });

  try {
    const existing = await db
      .select({ id: users.id })
      .from(users)
      .where(eq(users.email, DEV_EMAIL))
      .limit(1);

    if (existing.length) {
      console.log(`Dev user already exists (${DEV_EMAIL}). No changes.`);
      console.log(`Password (unchanged): ${DEV_PASSWORD}`);
      return;
    }

    const hashed = await bcrypt.hash(DEV_PASSWORD, 10);

    await db.transaction(async (tx) => {
      const [u] = await tx
        .insert(users)
        .values({
          email: DEV_EMAIL,
          hashedPassword: hashed,
          fullName: DEV_FULL_NAME,
        })
        .returning({ id: users.id });

      const baseSlug = slugifyOrg(DEV_ORG_NAME) || "dev-org";
      let orgSlug = baseSlug;
      for (let attempt = 0; attempt < 16; attempt++) {
        if (attempt > 0) {
          orgSlug = `${baseSlug}-${randomBytes(3).toString("hex")}`;
        }
        const clash = await tx
          .select({ id: organizations.id })
          .from(organizations)
          .where(eq(organizations.slug, orgSlug))
          .limit(1);
        if (!clash.length) break;
        if (attempt === 15) {
          throw new Error("Could not allocate a unique organization slug.");
        }
      }

      const [org] = await tx
        .insert(organizations)
        .values({
          name: DEV_ORG_NAME,
          slug: orgSlug,
        })
        .returning({ id: organizations.id });

      const [ws] = await tx
        .insert(workspaces)
        .values({
          name: "Default",
          slug: "default",
          organizationId: org.id,
        })
        .returning({ id: workspaces.id });

      await tx.insert(memberships).values({
        userId: u.id,
        organizationId: org.id,
        workspaceId: ws.id,
        role: "owner",
      });
    });

    console.log("Dev user created.");
    console.log(`  Email:    ${DEV_EMAIL}`);
    console.log(`  Password: ${DEV_PASSWORD}`);
    console.log(`  Org:      ${DEV_ORG_NAME}`);
  } finally {
    await client.end();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
