import {
  CanActivate,
  ExecutionContext,
  Injectable,
  NotFoundException,
  UnauthorizedException,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";

/**
 * Allows Shop Connect debug routes when APP_ENV !== production, or in production
 * when INTERNAL_CRON_SECRET is set and request sends matching X-Cron-Secret.
 */
@Injectable()
export class ShopConnectDebugGuard implements CanActivate {
  constructor(private readonly config: ConfigService) {}

  canActivate(context: ExecutionContext): boolean {
    const appEnv = this.config.get<string>("APP_ENV") ?? "development";
    if (appEnv !== "production") {
      return true;
    }

    const expected = this.config.get<string>("INTERNAL_CRON_SECRET")?.trim();
    if (!expected) {
      throw new NotFoundException();
    }

    const req = context.switchToHttp().getRequest<{
      headers: Record<string, string | string[] | undefined>;
    }>();
    const raw =
      req.headers["x-cron-secret"] ?? req.headers["X-Cron-Secret"];
    const secret = Array.isArray(raw) ? raw[0] : raw;

    if (!secret || secret !== expected) {
      throw new UnauthorizedException("Invalid or missing X-Cron-Secret");
    }

    return true;
  }
}
