import { ConfigService } from "@nestjs/config";
import { UnauthorizedException } from "@nestjs/common";
import { describe, expect, it } from "vitest";
import { ShopConnectDebugGuard } from "./shop-connect-debug.guard";

function execCtx(headers: Record<string, string | undefined>) {
  return {
    switchToHttp: () => ({
      getRequest: () => ({ headers }),
    }),
  };
}

describe("ShopConnectDebugGuard", () => {
  it("allows non-production without cron header", () => {
    const guard = new ShopConnectDebugGuard({
      get: (k: string) => (k === "APP_ENV" ? "staging" : undefined),
    } as unknown as ConfigService);
    expect(guard.canActivate(execCtx({}) as never)).toBe(true);
  });

  it("allows development when APP_ENV unset (defaults in guard)", () => {
    const guard = new ShopConnectDebugGuard({
      get: () => undefined,
    } as unknown as ConfigService);
    expect(guard.canActivate(execCtx({}) as never)).toBe(true);
  });

  it("production accepts matching X-Cron-Secret", () => {
    const guard = new ShopConnectDebugGuard({
      get: (k: string) => {
        if (k === "APP_ENV") return "production";
        if (k === "INTERNAL_CRON_SECRET") return "secret-secret";
        return undefined;
      },
    } as unknown as ConfigService);
    expect(
      guard.canActivate(
        execCtx({ "x-cron-secret": "secret-secret" }) as never,
      ),
    ).toBe(true);
  });

  it("production rejects wrong secret", () => {
    const guard = new ShopConnectDebugGuard({
      get: (k: string) => {
        if (k === "APP_ENV") return "production";
        if (k === "INTERNAL_CRON_SECRET") return "expected";
        return undefined;
      },
    } as unknown as ConfigService);
    expect(() =>
      guard.canActivate(execCtx({ "x-cron-secret": "wrong" }) as never),
    ).toThrow(UnauthorizedException);
  });
});
