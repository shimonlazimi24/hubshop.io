import {
  Controller,
  Get,
  HttpException,
  InternalServerErrorException,
  Query,
  Req,
  Res,
  UseGuards,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import type { Response } from "express";
import { AuthGuard } from "@nestjs/passport";
import type { AccessJwtPayload } from "../auth/jwt.strategy";
import { WorkspaceCtx } from "../tenancy/workspace.decorators";
import type {
  FrodoRequest,
  WorkspaceRequestContext,
} from "../tenancy/workspace-context";
import { WorkspaceMembershipGuard } from "../tenancy/workspace-membership.guard";
import { ConnectService } from "./connect.service";

function oauthRedirectErrorParam(e: unknown): string {
  if (e instanceof HttpException) {
    const r = e.getResponse();
    if (typeof r === "string") {
      return r;
    }
    if (typeof r === "object" && r !== null && "message" in r) {
      const m = (r as { message: string | string[] }).message;
      return Array.isArray(m) ? (m[0] ?? "oauth_failed") : String(m);
    }
  }
  if (e instanceof Error) {
    return e.message;
  }
  return "oauth_failed";
}

@Controller("connect")
export class ConnectController {
  constructor(
    private readonly connect: ConnectService,
    private readonly config: ConfigService,
  ) {}

  @Get("shop/authorize")
  @UseGuards(AuthGuard("jwt"), WorkspaceMembershipGuard)
  shopAuthorize(
    @Req() req: FrodoRequest & { user: AccessJwtPayload },
  ) {
    const ws = req.workspaceContext;
    if (!ws) {
      throw new InternalServerErrorException("workspace context missing");
    }
    return this.connect.buildShopAuthorizeForWorkspace({
      workspaceId: ws.workspaceId,
      userId: req.user.sub,
    });
  }

  /** Browser redirect from TikTok — validates signed state, exchanges code, redirects to SPA with result. */
  @Get("shop/callback")
  async shopCallback(
    @Query("code") code: string | undefined,
    @Query("state") state: string | undefined,
    @Res() res: Response,
  ) {
    const web =
      this.config.get<string>("PUBLIC_WEB_ORIGIN") ?? "http://localhost:5173";
    if (!code?.trim() || !state?.trim()) {
      return res.redirect(
        302,
        `${web}/connect/shop/result?error=missing_params`,
      );
    }
    try {
      await this.connect.completeShopOAuth(code.trim(), state.trim());
      return res.redirect(302, `${web}/connect/shop/result?status=connected`);
    } catch (e) {
      const msg = oauthRedirectErrorParam(e);
      return res.redirect(
        302,
        `${web}/connect/shop/result?error=${encodeURIComponent(msg)}`,
      );
    }
  }

  @Get("shop/status")
  @UseGuards(AuthGuard("jwt"), WorkspaceMembershipGuard)
  shopStatus(@WorkspaceCtx() ws: WorkspaceRequestContext) {
    return this.connect.listConnectedShops(ws.workspaceId);
  }
}
