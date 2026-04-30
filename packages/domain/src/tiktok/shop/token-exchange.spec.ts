import { describe, expect, it, vi } from "vitest";
import { exchangeShopAuthorizedCode } from "./token-exchange";

describe("exchangeShopAuthorizedCode", () => {
  it("parses TikTok-shaped JSON and returns tokens", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          code: 0,
          message: "success",
          data: {
            access_token: "atk",
            refresh_token: "rtk",
            access_token_expire_in: 3600,
            open_id: "seller-open-1",
            scope: "seller.authorization.info",
          },
          request_id: "rid",
        }),
        { status: 200 },
      ),
    );

    const out = await exchangeShopAuthorizedCode({
      tokenUrl: "https://auth.example.test/api/v2/token/get",
      appKey: "k",
      appSecret: "s",
      authCode: "code123",
      fetchImpl: fetchMock,
    });

    expect(out.accessToken).toBe("atk");
    expect(out.refreshToken).toBe("rtk");
    expect(out.sellerOpenId).toBe("seller-open-1");
    expect(out.accessTokenExpireInSec).toBe(3600);

    const calledUrl = fetchMock.mock.calls[0]?.[0] as string;
    expect(calledUrl).toContain("auth_code=code123");
    expect(calledUrl).toContain("grant_type=authorized_code");
    expect(calledUrl).not.toContain("atk");
  });

  it("throws on TikTok business error code", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ code: 40002, message: "bad_code" }), {
        status: 200,
      }),
    );

    await expect(
      exchangeShopAuthorizedCode({
        tokenUrl: "https://auth.example.test/get",
        appKey: "k",
        appSecret: "s",
        authCode: "x",
        fetchImpl: fetchMock,
      }),
    ).rejects.toThrow(/bad_code|40002/);
  });
});
