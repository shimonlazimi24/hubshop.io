import {
  Body,
  Controller,
  Get,
  HttpCode,
  Post,
  Req,
  UseGuards,
} from "@nestjs/common";
import type { Request } from "express";
import { AuthGuard } from "@nestjs/passport";
import { AuthService } from "./auth.service";
import { LoginDto, RefreshDto, RegisterDto } from "./dto";
import type { AccessJwtPayload } from "./jwt.strategy";

@Controller("auth")
export class AuthController {
  constructor(private readonly auth: AuthService) {}

  @Post("register")
  @HttpCode(201)
  async register(@Body() body: RegisterDto) {
    return this.auth.register({
      email: body.email,
      password: body.password,
      full_name: body.full_name,
      organization_name: body.organization_name,
    });
  }

  @Post("login")
  async login(@Body() body: LoginDto) {
    return this.auth.login(body.email, body.password);
  }

  @Post("refresh")
  async refresh(@Body() body: RefreshDto) {
    return this.auth.refresh(body.refresh_token);
  }

  @Post("logout")
  @HttpCode(200)
  async logout(@Req() req: Request) {
    const authHeader = req.headers.authorization ?? "";
    if (!authHeader.startsWith("Bearer ")) {
      return { ok: true };
    }
    const token = authHeader.slice(7);
    await this.auth.logout(token);
    return { ok: true };
  }

  @Get("me")
  @UseGuards(AuthGuard("jwt"))
  async me(@Req() req: Request & { user: AccessJwtPayload }) {
    const userId = req.user.sub;
    return {
      id: userId,
      claims: req.user,
    };
  }
}
