import {
  boolean,
  index,
  integer,
  jsonb,
  pgTable,
  text,
  timestamp,
  unique,
  uuid,
  varchar,
} from "drizzle-orm/pg-core";
import {
  accountStatusEnum,
  orderStatusEnum,
  platformEnum,
  productStatusEnum,
  roleEnum,
  syncJobStatusEnum,
  webhookStatusEnum,
} from "./enums";

export const users = pgTable("users", {
  id: uuid("id").defaultRandom().primaryKey(),
  email: varchar("email", { length: 255 }).notNull().unique(),
  hashedPassword: varchar("hashed_password", { length: 255 }),
  fullName: varchar("full_name", { length: 255 }).notNull(),
  isActive: boolean("is_active").notNull().default(true),
  isSuperuser: boolean("is_superuser").notNull().default(false),
  createdAt: timestamp("created_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
});

export const organizations = pgTable("organizations", {
  id: uuid("id").defaultRandom().primaryKey(),
  name: varchar("name", { length: 255 }).notNull(),
  slug: varchar("slug", { length: 255 }).notNull().unique(),
  createdAt: timestamp("created_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
});

export const workspaces = pgTable(
  "workspaces",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    name: varchar("name", { length: 255 }).notNull(),
    slug: varchar("slug", { length: 255 }).notNull(),
    organizationId: uuid("organization_id")
      .notNull()
      .references(() => organizations.id, { onDelete: "cascade" }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (t) => [unique("uq_workspace_org_slug").on(t.organizationId, t.slug)],
);

export const memberships = pgTable(
  "memberships",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    organizationId: uuid("organization_id")
      .notNull()
      .references(() => organizations.id, { onDelete: "cascade" }),
    workspaceId: uuid("workspace_id").references(() => workspaces.id, {
      onDelete: "cascade",
    }),
    role: roleEnum("role").notNull().default("member"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (t) => [
    unique("uq_membership").on(t.userId, t.organizationId, t.workspaceId),
  ],
);

export const webhookEvents = pgTable(
  "webhook_events",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    platform: platformEnum("platform").notNull(),
    eventType: varchar("event_type", { length: 255 }).notNull(),
    idempotencyKey: varchar("idempotency_key", { length: 255 }).notNull().unique(),
    payload: jsonb("payload").notNull(),
    status: webhookStatusEnum("status").notNull().default("received"),
    errorMessage: text("error_message"),
    workspaceId: uuid("workspace_id").references(() => workspaces.id, {
      onDelete: "set null",
    }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
);

export const connectedAccounts = pgTable(
  "connected_accounts",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    workspaceId: uuid("workspace_id")
      .notNull()
      .references(() => workspaces.id, { onDelete: "cascade" }),
    platform: platformEnum("platform").notNull(),
    platformAccountId: varchar("platform_account_id", { length: 255 }).notNull(),
    platformAccountName: varchar("platform_account_name", { length: 255 }),
    status: accountStatusEnum("status").notNull().default("active"),
    identityGroupId: uuid("identity_group_id"),
    metadataJson: jsonb("metadata_json"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (t) => [
    index("ix_connected_accounts_workspace").on(t.workspaceId),
    unique("uq_connected_accounts_workspace_platform_account").on(
      t.workspaceId,
      t.platform,
      t.platformAccountId,
    ),
  ],
);

export const tokenVault = pgTable("token_vault", {
  id: uuid("id").defaultRandom().primaryKey(),
  connectedAccountId: uuid("connected_account_id")
    .notNull()
    .unique()
    .references(() => connectedAccounts.id, { onDelete: "cascade" }),
  encryptedAccessToken: text("encrypted_access_token").notNull(),
  encryptedRefreshToken: text("encrypted_refresh_token"),
  accessTokenExpiresAt: varchar("access_token_expires_at", { length: 50 }),
  refreshTokenExpiresAt: varchar("refresh_token_expires_at", { length: 50 }),
  scopes: text("scopes"),
  createdAt: timestamp("created_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
});

export const syncJobs = pgTable(
  "sync_jobs",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    workspaceId: uuid("workspace_id")
      .notNull()
      .references(() => workspaces.id, { onDelete: "cascade" }),
    connectedAccountId: uuid("connected_account_id")
      .notNull()
      .references(() => connectedAccounts.id, { onDelete: "cascade" }),
    platform: varchar("platform", { length: 50 }).notNull(),
    syncType: varchar("sync_type", { length: 50 }).notNull(),
    status: syncJobStatusEnum("status").notNull().default("pending"),
    itemsSynced: integer("items_synced").notNull().default(0),
    itemsTotal: integer("items_total"),
    errorMessage: text("error_message"),
    startedAt: timestamp("started_at", { withTimezone: true }),
    completedAt: timestamp("completed_at", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (t) => [index("ix_sync_jobs_workspace").on(t.workspaceId)],
);

export const shops = pgTable(
  "shops",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    workspaceId: uuid("workspace_id")
      .notNull()
      .references(() => workspaces.id, { onDelete: "cascade" }),
    connectedAccountId: uuid("connected_account_id")
      .notNull()
      .references(() => connectedAccounts.id, { onDelete: "cascade" }),
    shopId: varchar("shop_id", { length: 255 }).notNull().unique(),
    shopCipher: varchar("shop_cipher", { length: 255 }).notNull(),
    shopName: varchar("shop_name", { length: 255 }).notNull(),
    region: varchar("region", { length: 10 }).notNull(),
    lastProductSyncAt: timestamp("last_product_sync_at", { withTimezone: true }),
    lastOrderSyncAt: timestamp("last_order_sync_at", { withTimezone: true }),
    /** TikTok list/search paging cursor for product sync jobs. */
    productSyncCursor: text("product_sync_cursor"),
    /** TikTok list/search paging cursor for order sync jobs. */
    orderSyncCursor: text("order_sync_cursor"),
    /** Latest raw shop payload from TikTok authorization/shops (debugging). */
    discoverySnapshotJson: jsonb("discovery_snapshot_json"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (t) => [index("ix_shops_workspace").on(t.workspaceId)],
);

export const products = pgTable(
  "products",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    workspaceId: uuid("workspace_id")
      .notNull()
      .references(() => workspaces.id, { onDelete: "cascade" }),
    shopId: uuid("shop_id")
      .notNull()
      .references(() => shops.id, { onDelete: "cascade" }),
    platformProductId: varchar("platform_product_id", { length: 255 }).notNull(),
    title: varchar("title", { length: 500 }).notNull(),
    status: productStatusEnum("status").notNull().default("draft"),
    mainImageUrl: text("main_image_url"),
    priceAmount: varchar("price_amount", { length: 20 }),
    currency: varchar("currency", { length: 3 }),
    inventoryTotal: integer("inventory_total").notNull().default(0),
    skuCount: integer("sku_count").notNull().default(0),
    detailJson: jsonb("detail_json"),
    /** Last TikTok API row snapshot for this product (debugging / forward compat). */
    apiSnapshotJson: jsonb("api_snapshot_json"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (t) => [
    unique("uq_products_shop_platform").on(t.shopId, t.platformProductId),
    index("ix_products_workspace_status").on(t.workspaceId, t.status),
    index("ix_products_workspace_created").on(t.workspaceId, t.createdAt),
  ],
);

export const orders = pgTable(
  "orders",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    workspaceId: uuid("workspace_id")
      .notNull()
      .references(() => workspaces.id, { onDelete: "cascade" }),
    shopId: uuid("shop_id")
      .notNull()
      .references(() => shops.id, { onDelete: "cascade" }),
    platformOrderId: varchar("platform_order_id", { length: 255 }).notNull(),
    status: orderStatusEnum("status").notNull().default("unpaid"),
    totalAmount: varchar("total_amount", { length: 20 }).notNull(),
    currency: varchar("currency", { length: 3 }).notNull().default("USD"),
    itemCount: integer("item_count").notNull().default(0),
    fulfillmentType: varchar("fulfillment_type", { length: 50 }),
    rtsSla: timestamp("rts_sla", { withTimezone: true }),
    detailJson: jsonb("detail_json"),
    apiSnapshotJson: jsonb("api_snapshot_json"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (t) => [
    unique("uq_orders_shop_platform").on(t.shopId, t.platformOrderId),
    index("ix_orders_workspace_status").on(t.workspaceId, t.status),
    index("ix_orders_workspace_created").on(t.workspaceId, t.createdAt),
  ],
);

/** Frodo v2: dedupe scheduled fan-out (additive migration). */
export const scheduledJobRuns = pgTable(
  "scheduled_job_runs",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    jobKey: text("job_key").notNull(),
    periodBucket: text("period_bucket").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (t) => [unique("scheduled_job_runs_job_key_period").on(t.jobKey, t.periodBucket)],
);

/** Frodo v2: strangler feature flags per workspace. */
export const featureFlags = pgTable(
  "feature_flags",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    workspaceId: uuid("workspace_id")
      .notNull()
      .references(() => workspaces.id, { onDelete: "cascade" }),
    flagKey: varchar("flag_key", { length: 128 }).notNull(),
    enabled: boolean("enabled").notNull().default(false),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (t) => [
    unique("feature_flags_workspace_flag").on(t.workspaceId, t.flagKey),
    index("ix_feature_flags_workspace").on(t.workspaceId),
  ],
);
