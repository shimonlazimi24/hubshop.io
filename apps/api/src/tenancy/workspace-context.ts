import type { Request } from "express";

export interface WorkspaceRequestContext {
  workspaceId: string;
  organizationId: string;
  membershipId: string;
  role: string;
}

export type FrodoRequest = Request & {
  workspaceContext?: WorkspaceRequestContext;
  /** raw JSON body bytes for webhook signature/idempotency (POST /webhooks/*). */
  rawBody?: Buffer;
};
