"use client";

import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { useCallback } from "react";

export function usePlatformFilter(defaultValue = "all") {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const platform = searchParams.get("platform") ?? defaultValue;

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
