import { Global, Module } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { createDb } from "@frodo/db";

export const DRIZZLE = Symbol("DRIZZLE");

@Global()
@Module({
  providers: [
    {
      provide: DRIZZLE,
      inject: [ConfigService],
      useFactory: (config: ConfigService) => {
        const url = config.get<string>("DATABASE_URL");
        if (!url?.trim()) {
          throw new Error(
            "DATABASE_URL is required: set the PostgreSQL connection string for API runtime (not DATABASE_MIGRATION_URL alone — see docs/v2/ENVIRONMENT.md).",
          );
        }
        return createDb(url);
      },
    },
  ],
  exports: [DRIZZLE],
})
export class DatabaseModule {}
