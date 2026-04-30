import { Controller, Get } from "@nestjs/common";

@Controller("health")
export class HealthController {
  @Get()
  getHealth(): { ok: boolean; service: string } {
    return { ok: true, service: "frodo-api" };
  }
}
