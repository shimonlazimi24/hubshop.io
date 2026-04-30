import { loadApiEnv } from "@frodo/config";
import { ValidationPipe } from "@nestjs/common";
import { NestFactory } from "@nestjs/core";
import type { NestExpressApplication } from "@nestjs/platform-express";
import cookieParser from "cookie-parser";
import { json, urlencoded } from "express";
import { AppModule } from "./app.module";
import type { FrodoRequest } from "./tenancy/workspace-context";

async function bootstrap(): Promise<void> {
  try {
    loadApiEnv(process.env);
  } catch (e) {
    console.error(e instanceof Error ? e.message : e);
    console.error(
      "API startup requires valid environment (DATABASE_URL, JWT_SECRET, …). See docs/v2/ENVIRONMENT.md.",
    );
    process.exit(1);
    return;
  }

  const app = await NestFactory.create<NestExpressApplication>(AppModule, {
    bodyParser: false,
  });

  app.use(
    json({
      limit: "2mb",
      verify: (req: FrodoRequest, _res, buf: Buffer) => {
        if (
          req.originalUrl?.includes("/webhooks/") &&
          req.method === "POST"
        ) {
          req.rawBody = Buffer.from(buf);
        }
      },
    }),
  );
  app.use(urlencoded({ extended: true, limit: "2mb" }));

  app.setGlobalPrefix("api");
  app.use(cookieParser());
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
    }),
  );
  const origin = process.env.PUBLIC_WEB_ORIGIN ?? "http://localhost:5173";
  app.enableCors({
    origin: [origin],
    credentials: true,
    methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allowedHeaders: [
      "Authorization",
      "Content-Type",
      "X-Workspace-Id",
      "X-Cron-Secret",
      "X-Requested-With",
    ],
  });
  const port = Number(process.env.PORT ?? 8001);
  await app.listen(port);
}

bootstrap();
