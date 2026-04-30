import { Injectable, UnauthorizedException } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { PassportStrategy } from "@nestjs/passport";
import { ExtractJwt, Strategy } from "passport-jwt";
import { RedisService } from "../redis/redis.service";

export interface AccessJwtPayload {
  sub: string;
  type?: string;
  jti?: string;
  org_id?: string;
  role?: string;
}

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy, "jwt") {
  constructor(
    config: ConfigService,
    private readonly redis: RedisService,
  ) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: config.get<string>("JWT_SECRET"),
    });
  }

  async validate(payload: AccessJwtPayload): Promise<AccessJwtPayload> {
    if (payload.type && payload.type !== "access") {
      throw new UnauthorizedException("Invalid token type");
    }
    if (payload.jti) {
      const blacklisted = await this.redis.exists(
        `blacklisted_token:${payload.jti}`,
      );
      if (blacklisted) {
        throw new UnauthorizedException("Token revoked");
      }
    }
    return payload;
  }
}
