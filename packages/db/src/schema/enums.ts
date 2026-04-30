import { pgEnum } from "drizzle-orm/pg-core";

/** Matches PostgreSQL `role_enum` from legacy SQLAlchemy models. */
export const roleEnum = pgEnum("role_enum", [
  "owner",
  "admin",
  "manager",
  "member",
  "viewer",
]);

export const platformEnum = pgEnum("platform_enum", [
  "shop",
  "developer",
  "marketing",
  "live",
  "research",
]);

export const webhookStatusEnum = pgEnum("webhook_status_enum", [
  "received",
  "processing",
  "processed",
  "failed",
]);

export const accountStatusEnum = pgEnum("account_status_enum", [
  "active",
  "error",
  "disconnected",
  "refreshing",
]);

export const syncJobStatusEnum = pgEnum("sync_job_status_enum", [
  "pending",
  "running",
  "completed",
  "failed",
]);

export const productStatusEnum = pgEnum("product_status_enum", [
  "draft",
  "pending",
  "live",
  "seller_deactivated",
  "platform_deactivated",
  "frozen",
  "deleted",
]);

export const orderStatusEnum = pgEnum("order_status_enum", [
  "unpaid",
  "on_hold",
  "awaiting_shipment",
  "awaiting_collection",
  "partially_shipping",
  "in_transit",
  "delivered",
  "completed",
  "cancelled",
]);
