import {
  Controller,
  Get,
  Param,
  Post,
  UseGuards,
} from "@nestjs/common";
import { AuthGuard } from "@nestjs/passport";
import { WorkspaceCtx } from "../tenancy/workspace.decorators";
import type { WorkspaceRequestContext } from "../tenancy/workspace-context";
import { parseUuidParam } from "../tenancy/parse-uuid";
import { WorkspaceMembershipGuard } from "../tenancy/workspace-membership.guard";
import { CommerceService } from "./commerce.service";

@Controller("commerce")
@UseGuards(AuthGuard("jwt"), WorkspaceMembershipGuard)
export class CommerceController {
  constructor(private readonly commerce: CommerceService) {}

  @Post("shops/:shopId/sync-products")
  async syncProducts(
    @WorkspaceCtx() ws: WorkspaceRequestContext,
    @Param("shopId") shopId: string,
  ) {
    const sid = parseUuidParam("shopId", shopId);
    return this.commerce.enqueueSyncProducts(ws.workspaceId, sid);
  }

  @Post("shops/:shopId/sync-orders")
  async syncOrders(
    @WorkspaceCtx() ws: WorkspaceRequestContext,
    @Param("shopId") shopId: string,
  ) {
    const sid = parseUuidParam("shopId", shopId);
    return this.commerce.enqueueSyncOrders(ws.workspaceId, sid);
  }

  @Get("shops/:shopId/sync-status")
  async syncStatus(
    @WorkspaceCtx() ws: WorkspaceRequestContext,
    @Param("shopId") shopId: string,
  ) {
    const sid = parseUuidParam("shopId", shopId);
    return this.commerce.getShopSyncStatus(ws.workspaceId, sid);
  }

  @Get("shops/:shopId/products")
  async listProducts(
    @WorkspaceCtx() ws: WorkspaceRequestContext,
    @Param("shopId") shopId: string,
  ) {
    const sid = parseUuidParam("shopId", shopId);
    const productsList = await this.commerce.listProducts(
      ws.workspaceId,
      sid,
    );
    return { shopId: sid, products: productsList };
  }

  @Get("shops/:shopId/orders")
  async listOrders(
    @WorkspaceCtx() ws: WorkspaceRequestContext,
    @Param("shopId") shopId: string,
  ) {
    const sid = parseUuidParam("shopId", shopId);
    const ordersList = await this.commerce.listOrders(ws.workspaceId, sid);
    return { shopId: sid, orders: ordersList };
  }
}
