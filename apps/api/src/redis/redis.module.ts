import { Global, Module } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { RedisStartup } from "./redis-startup";
import { RedisService } from "./redis.service";

@Global()
@Module({
  providers: [
    {
      provide: RedisService,
      inject: [ConfigService],
      useFactory: (config: ConfigService) => {
        const url = config.get<string>("REDIS_URL");
        return new RedisService(url);
      },
    },
    RedisStartup,
  ],
  exports: [RedisService],
})
export class RedisModule {}
