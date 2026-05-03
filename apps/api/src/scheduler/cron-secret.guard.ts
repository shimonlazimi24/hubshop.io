import {
  CanActivate,
  ExecutionContext,
  Injectable,
  UnauthorizedException,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";

@Injectable()
export class CronSecretGuard implements CanActivate {
  constructor(private readonly config: ConfigService) {}

  canActivate(context: ExecutionContext): boolean {
    const req = context.switchToHttp().getRequest<{
      headers: Record<string, string | string[] | undefined>;
    }>();
    const raw =
      req.headers["x-cron-secret"] ?? req.headers["X-Cron-Secret"];
    const secret = Array.isArray(raw) ? raw[0] : raw;
    const expected = this.config.get<string>("INTERNAL_CRON_SECRET")?.trim();
    if (!expected || secret !== expected) {
      throw new UnauthorizedException("Invalid cron secret");
    }
    return true;
  }
}
