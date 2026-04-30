/** Remove token-like strings from objects for safe logs. */
export function redactForLog(input: unknown): unknown {
  if (input === null || input === undefined) {
    return input;
  }
  if (typeof input === "string") {
    if (input.length > 12 && /^[\w-]+$/.test(input)) {
      return `${input.slice(0, 4)}…${input.slice(-2)}`;
    }
    return input;
  }
  if (Array.isArray(input)) {
    return input.map(redactForLog);
  }
  if (typeof input === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(input as Record<string, unknown>)) {
      const lk = k.toLowerCase();
      if (
        lk === "sign" ||
        lk.includes("token") ||
        lk.includes("secret") ||
        lk.includes("cipher")
      ) {
        out[k] = "[redacted]";
      } else {
        out[k] = redactForLog(v);
      }
    }
    return out;
  }
  return input;
}
