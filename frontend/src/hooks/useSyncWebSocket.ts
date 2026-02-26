"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api";

export interface SyncWSMessage {
  type: "sync_progress" | "sync_complete" | "sync_failed";
  platform: string;
  sync_type: string;
  items_synced: number;
  items_total: number | null;
  error?: string;
}

interface UseSyncWebSocketOptions {
  workspaceId: string;
  token: string | null;
  onMessage?: (message: SyncWSMessage) => void;
}

export function useSyncWebSocket({
  workspaceId,
  token,
  onMessage,
}: UseSyncWebSocketOptions) {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    if (!token || !workspaceId) return;

    const url = `${WS_BASE}/connect/ws/${workspaceId}?token=${token}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);

    ws.onmessage = (event) => {
      try {
        const message: SyncWSMessage = JSON.parse(event.data);
        onMessageRef.current?.(message);
      } catch {
        // Ignore malformed messages
      }
    };

    ws.onclose = () => {
      setConnected(false);
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => ws.close();
  }, [token, workspaceId]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { connected };
}
