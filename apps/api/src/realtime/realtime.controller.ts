import {
  Controller,
  MessageEvent,
  Sse,
  UseGuards,
} from "@nestjs/common";
import { AuthGuard } from "@nestjs/passport";
import { interval, map, merge, Observable } from "rxjs";
import { RedisService } from "../redis/redis.service";
import { WorkspaceCtx } from "../tenancy/workspace.decorators";
import type { WorkspaceRequestContext } from "../tenancy/workspace-context";
import { WorkspaceMembershipGuard } from "../tenancy/workspace-membership.guard";

/**
 * SSE stream scoped to a workspace the caller belongs to.
 * Client must send Authorization Bearer and workspaceId as query (guard reads query.workspaceId).
 * Note: native EventSource cannot set Authorization; use fetch-based SSE or cookies for browsers.
 */
@Controller("realtime")
@UseGuards(AuthGuard("jwt"), WorkspaceMembershipGuard)
export class RealtimeController {
  constructor(private readonly redis: RedisService) {}

  @Sse("events/stream")
  stream(
    @WorkspaceCtx() ws: WorkspaceRequestContext,
  ): Observable<MessageEvent> {
    const workspaceId = ws.workspaceId;

    const heartbeats = interval(30000).pipe(
      map(
        (): MessageEvent =>
          ({ data: { type: "heartbeat", ts: Date.now() } }) as MessageEvent,
      ),
    );

    if (!this.redis.isEnabled()) {
      return heartbeats;
    }

    return merge(
      heartbeats,
      new Observable<MessageEvent>((sub) => {
        const subClient = this.redis.getSubscriber();
        if (!subClient) {
          sub.complete();
          return;
        }
        const channel = `frodo:workspace:${workspaceId}`;
        subClient.subscribe(channel, (err) => {
          if (err) {
            sub.error(err);
          }
        });
        subClient.on("message", (ch, message) => {
          if (ch === channel) {
            sub.next({ data: message } as MessageEvent);
          }
        });
        return () => {
          void subClient.unsubscribe(channel);
          subClient.disconnect();
        };
      }),
    );
  }
}
