import {
  BadRequestException,
  ConflictException,
  Injectable,
  UnauthorizedException,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { JwtService } from "@nestjs/jwt";
import {
  memberships,
  organizations,
  users,
  workspaces,
} from "@frodo/db";
import { randomBytes, randomUUID } from "node:crypto";
import bcrypt from "bcrypt";
import { eq } from "drizzle-orm";
import type { FrodoDb } from "@frodo/db";
import { RedisService } from "../redis/redis.service";
import { DRIZZLE } from "../database/database.module";
import { Inject } from "@nestjs/common";

const PASSWORD_PATTERN = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/;

function validatePassword(password: string): void {
  if (password.length < 8 || !PASSWORD_PATTERN.test(password)) {
    throw new BadRequestException(
      "Password must be at least 8 characters and contain at least one uppercase letter, one lowercase letter, and one digit.",
    );
  }
}

function slugifyOrg(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "")
    .slice(0, 50);
}

@Injectable()
export class AuthService {
  constructor(
    @Inject(DRIZZLE) private readonly db: FrodoDb,
    private readonly jwt: JwtService,
    private readonly config: ConfigService,
    private readonly redis: RedisService,
  ) {}

  private signAccess(
    userId: string,
    orgId?: string,
    role?: string,
  ): string {
    return this.jwt.sign(
      {
        sub: userId,
        type: "access",
        jti: randomUUID(),
        ...(orgId ? { org_id: orgId } : {}),
        ...(role ? { role } : {}),
      },
      {
        expiresIn: `${this.config.get<number>("JWT_ACCESS_EXPIRE_MINUTES") ?? 15}m`,
      },
    );
  }

  private signRefresh(userId: string): string {
    return this.jwt.sign(
      {
        sub: userId,
        type: "refresh",
        jti: randomUUID(),
      },
      {
        expiresIn: `${this.config.get<number>("JWT_REFRESH_EXPIRE_DAYS") ?? 7}d`,
      },
    );
  }

  async register(input: {
    email: string;
    password: string;
    full_name: string;
    organization_name: string;
  }): Promise<{ access_token: string; refresh_token: string }> {
    validatePassword(input.password);

    const existing = await this.db
      .select({ id: users.id })
      .from(users)
      .where(eq(users.email, input.email))
      .limit(1);
    if (existing.length) {
      throw new ConflictException("Email already registered");
    }

    const hashed = await bcrypt.hash(input.password, 10);

    const out = await this.db.transaction(async (tx) => {
      const [u] = await tx
        .insert(users)
        .values({
          email: input.email,
          hashedPassword: hashed,
          fullName: input.full_name,
        })
        .returning({ id: users.id });

      const baseSlug = slugifyOrg(input.organization_name) || "org";
      let orgSlug = baseSlug;
      for (let attempt = 0; attempt < 16; attempt++) {
        if (attempt > 0) {
          orgSlug = `${baseSlug}-${randomBytes(3).toString("hex")}`;
        }
        const clash = await tx
          .select({ id: organizations.id })
          .from(organizations)
          .where(eq(organizations.slug, orgSlug))
          .limit(1);
        if (!clash.length) {
          break;
        }
        if (attempt === 15) {
          throw new ConflictException(
            "Could not create organization — try a different organization name.",
          );
        }
      }

      const [org] = await tx
        .insert(organizations)
        .values({
          name: input.organization_name,
          slug: orgSlug,
        })
        .returning({ id: organizations.id });

      const [ws] = await tx
        .insert(workspaces)
        .values({
          name: "Default",
          slug: "default",
          organizationId: org.id,
        })
        .returning({ id: workspaces.id });

      await tx.insert(memberships).values({
        userId: u.id,
        organizationId: org.id,
        workspaceId: ws.id,
        role: "owner",
      });

      return { userId: u.id, orgId: org.id, role: "owner" as const };
    });

    return {
      access_token: this.signAccess(out.userId, out.orgId, out.role),
      refresh_token: this.signRefresh(out.userId),
    };
  }

  async login(
    email: string,
    password: string,
  ): Promise<{ access_token: string; refresh_token: string }> {
    const rows = await this.db
      .select()
      .from(users)
      .where(eq(users.email, email))
      .limit(1);
    const user = rows[0];
    if (!user) {
      throw new UnauthorizedException("Invalid email or password");
    }
    if (!user.hashedPassword) {
      throw new BadRequestException(
        "This account uses social login. Please sign in with TikTok or Google.",
      );
    }
    const ok = await bcrypt.compare(password, user.hashedPassword);
    if (!ok) {
      throw new UnauthorizedException("Invalid email or password");
    }
    if (!user.isActive) {
      throw new UnauthorizedException("Account is disabled");
    }

    const [membership] = await this.db
      .select()
      .from(memberships)
      .where(eq(memberships.userId, user.id))
      .limit(1);

    return {
      access_token: this.signAccess(
        user.id,
        membership?.organizationId,
        membership?.role,
      ),
      refresh_token: this.signRefresh(user.id),
    };
  }

  async refresh(
    refreshToken: string,
  ): Promise<{ access_token: string; refresh_token: string }> {
    let payload: {
      sub?: string;
      type?: string;
      jti?: string;
      exp?: number;
    };
    try {
      payload = this.jwt.verify(refreshToken);
    } catch {
      throw new UnauthorizedException("Invalid or expired refresh token");
    }
    if (payload.type !== "refresh") {
      throw new UnauthorizedException("Invalid token type");
    }
    if (payload.jti && (await this.redis.exists(`blacklisted_token:${payload.jti}`))) {
      throw new UnauthorizedException("Refresh token has been revoked");
    }

    if (payload.jti && payload.exp) {
      const remaining = Math.max(0, payload.exp - Math.floor(Date.now() / 1000));
      if (remaining > 0) {
        await this.redis.setEx(`blacklisted_token:${payload.jti}`, remaining, "1");
      }
    }

    const userId = payload.sub;
    if (!userId) {
      throw new UnauthorizedException("Invalid token");
    }

    const [user] = await this.db
      .select()
      .from(users)
      .where(eq(users.id, userId))
      .limit(1);
    if (!user?.isActive) {
      throw new UnauthorizedException("User not found");
    }

    const [membership] = await this.db
      .select()
      .from(memberships)
      .where(eq(memberships.userId, user.id))
      .limit(1);

    return {
      access_token: this.signAccess(
        user.id,
        membership?.organizationId,
        membership?.role,
      ),
      refresh_token: this.signRefresh(user.id),
    };
  }

  async logout(accessToken: string): Promise<void> {
    let payload: { jti?: string; exp?: number };
    try {
      payload = this.jwt.verify(accessToken);
    } catch {
      throw new UnauthorizedException("Invalid or expired token");
    }
    if (!payload.jti) {
      throw new UnauthorizedException("Token missing jti claim");
    }
    if (payload.exp) {
      const remaining = Math.max(0, payload.exp - Math.floor(Date.now() / 1000));
      if (remaining > 0) {
        await this.redis.setEx(`blacklisted_token:${payload.jti}`, remaining, "1");
      }
    }
  }
}
