"use client";

import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { useCallback } from "react";

const VALID_PLATFORMS = new Set(["all", "marketing", "shop", "affiliate"]);

export function usePlatformFilter(defaultValue = "all") {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const raw = searchParams.get("platform") ?? defaultValue;
  const platform = VALID_PLATFORMS.has(raw) ? raw : defaultValue;

  const setPlatform = useCallback(
    (value: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (value === defaultValue) {
        params.delete("platform");
      } else {
        params.set("platform", value);
      }
      const qs = params.toString();
      router.push(qs ? `${pathname}?${qs}` : pathname);
    },
    [searchParams, router, pathname, defaultValue],
  );

  return { platform, setPlatform } as const;
}
