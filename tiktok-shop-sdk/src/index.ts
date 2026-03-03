import Fastify from "fastify";
import { registerRoutes } from "./router";

const app = Fastify({
  logger: {
    level: process.env.LOG_LEVEL || "info",
  },
  bodyLimit: 1_048_576, // 1MB max body
});

// Load credentials from environment
const appKey = process.env.TIKTOK_SHOP_APP_KEY;
const appSecret = process.env.TIKTOK_SHOP_APP_SECRET;
const sidecarAuthToken = process.env.SIDECAR_AUTH_TOKEN;

if (!appKey || !appSecret) {
  app.log.fatal("TIKTOK_SHOP_APP_KEY and TIKTOK_SHOP_APP_SECRET must be set");
  process.exit(1);
}

if (!sidecarAuthToken) {
  app.log.fatal("SIDECAR_AUTH_TOKEN must be set");
  process.exit(1);
}

// Configure SDK globals (used by discovery endpoint's registry)
const { ClientConfiguration } = require("../sdk/client/config");
ClientConfiguration.globalConfig.app_key = appKey;
ClientConfiguration.globalConfig.app_secret = appSecret;

// Health check — no auth required
app.get("/health", async () => ({ status: "ok" }));

// Register API routes
registerRoutes(app, appKey, appSecret, sidecarAuthToken);

const start = async () => {
  try {
    const port = parseInt(process.env.PORT || "4000", 10);
    await app.listen({ port, host: "0.0.0.0" });
    app.log.info(`TikTok Shop SDK sidecar listening on port ${port}`);
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();
