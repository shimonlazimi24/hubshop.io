import { describe, expect, it, vi } from "vitest";
import { fetchAuthorizedShops } from "./open-api";

describe("fetchAuthorizedShops", () => {
  it("normalizes shop rows from TikTok JSON", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          code: 0,
          data: {
            shops: [
              {
                id: "sid1",
                cipher: "cipher1",
                code: "SC01",
                name: "My Shop",
                region: "US",
                seller_type: "LOCAL",
              },
            ],
          },
          request_id: "r",
        }),
        { status: 200 },
      ),
    );

    const out = await fetchAuthorizedShops({
      openApiBase: "https://open-api.test",
      appKey: "k",
      appSecret: "secretsecretsecretsecret",
      accessToken: "tok",
      fetchImpl: fetchMock,
    });

    expect(out.shops).toHaveLength(1);
    expect(out.shops[0]?.shopId).toBe("sid1");
    expect(out.shops[0]?.shopCipher).toBe("cipher1");
    expect(out.shops[0]?.shopName).toBe("My Shop");
    expect(out.shops[0]?.region).toBe("US");

    const url = fetchMock.mock.calls[0]?.[0] as string;
    expect(url).toContain("/authorization/202309/shops");
    expect(url).toContain("sign=");
    expect(url).toContain("access_token=tok");
  });
});
