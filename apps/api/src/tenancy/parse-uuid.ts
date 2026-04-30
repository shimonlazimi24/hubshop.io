import { BadRequestException } from "@nestjs/common";

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function parseUuidParam(label: string, raw: string | undefined): string {
  if (!raw?.trim()) {
    throw new BadRequestException(`${label} is required`);
  }
  const v = raw.trim();
  if (!UUID_RE.test(v)) {
    throw new BadRequestException(`${label} must be a valid UUID`);
  }
  return v;
}
