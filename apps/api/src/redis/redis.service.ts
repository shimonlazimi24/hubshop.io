import { Injectable, Logger } from "@nestjs/common";
import Redis from "ioredis";

@Injectable()
export class RedisService {
  private readonly logger = new Logger(RedisService.name);
  private client: Redis | null = null;

  constructor(url: string | undefined) {
    if (url) {
      this.client = new Redis(url);
    } else {
      this.logger.warn("REDIS_URL not set — token blacklist and pub/sub disabled");
    }
  }

  isEnabled(): boolean {
    return this.client !== null;
  }

  async pingRequired(): Promise<void> {
    if (!this.client) {
      throw new Error(
        "Redis required for auth/realtime but REDIS_URL is not configured",
      );
    }
    const result = await this.client.ping();
    if (result !== "PONG") {
      throw new Error(`Redis PING failed: ${result}`);
    }
    this.logger.log("Redis connectivity verified");
  }

  async setEx(key: string, seconds: number, value: string): Promise<void> {
    if (!this.client) {
      return;
    }
    await this.client.setex(key, seconds, value);
  }

  async exists(key: string): Promise<boolean> {
    if (!this.client) {
      return false;
    }
    const n = await this.client.exists(key);
    return n > 0;
  }

  getSubscriber(): Redis | null {
    if (!this.client) {
      return null;
    }
    return this.client.duplicate();
  }

  async publish(channel: string, message: string): Promise<void> {
    if (!this.client) {
      return;
    }
    await this.client.publish(channel, message);
  }
}
