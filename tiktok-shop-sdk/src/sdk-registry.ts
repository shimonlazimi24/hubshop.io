import { API_OBJECT } from "../sdk/api/apis";

interface OperationInfo {
  domain: string;
  version: string;
  operation: string;
}

/**
 * Parse an API class name like "ProductV202502Api" into { domain: "product", version: "V202502" }
 */
function parseApiClassName(name: string): { domain: string; version: string } | null {
  const match = name.match(/^([A-Za-z]+?)(V\d{6})Api$/);
  if (!match) return null;
  return { domain: match[1].toLowerCase(), version: match[2] };
}

/**
 * List all available operations across all SDK API classes.
 * Returns a flat list of { domain, version, operations[] } grouped by domain+version.
 */
export function listAllOperations(): Array<{
  domain: string;
  version: string;
  operations: string[];
}> {
  const result: Array<{ domain: string; version: string; operations: string[] }> = [];

  for (const [apiName, ApiClass] of Object.entries(API_OBJECT)) {
    const parsed = parseApiClassName(apiName);
    if (!parsed) continue;

    const instance = new (ApiClass as any)() as any;
    const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(instance))
      .filter(
        (m) =>
          m !== "constructor" &&
          !m.startsWith("_") &&
          !m.startsWith("set") &&
          !m.startsWith("get") &&
          !m.startsWith("add") &&
          typeof instance[m] === "function"
      );

    result.push({
      domain: parsed.domain,
      version: parsed.version,
      operations: methods,
    });
  }

  return result.sort(
    (a, b) => a.domain.localeCompare(b.domain) || a.version.localeCompare(b.version)
  );
}
