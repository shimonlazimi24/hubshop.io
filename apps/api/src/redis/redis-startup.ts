import { Injectable, Logger, OnModuleInit } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { RedisService } from "./redis.service";

@Injectable()
export class RedisStartup implements OnModuleInit {
  private readonly logger = new Logger(RedisStartup.name);

  constructor(
    private readonly redis: RedisService,
    private readonly config: ConfigService,
  ) {}

  async onModuleInit(): Promise<void> {
    const requireRedis = this.config.get<boolean>("effectiveRequireRedis");
    if (!requireRedis) {
      this.logger.warn(
        "JWT blacklist/logout may not revoke tokens when Redis is disabled (development only)",
      );
      return;
    }
    await this.redis.pingRequired();
  }
}
