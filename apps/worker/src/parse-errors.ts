/** Detect Zod parse errors without importing `zod` in the worker bundle. */
export function isZodError(
  e: unknown,
): e is { name: "ZodError"; issues: unknown[] } {
  if (typeof e !== "object" || e === null) {
    return false;
  }
  const o = e as { name?: unknown; issues?: unknown };
  return o.name === "ZodError" && Array.isArray(o.issues);
}
