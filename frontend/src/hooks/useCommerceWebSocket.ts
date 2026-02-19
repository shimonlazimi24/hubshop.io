"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api";

export interface CommerceWSMessage {
  type: "order_status_change" | "package_update" | "return_status_change" | "cancellation_status_change";
  [key: string]: unknown;
}

interface UseCommerceWebSocketOptions {
  workspaceId: string;
  token: string | null;
  onMessage?: (message: CommerceWSMessage) => void;
}

export function useCommerceWebSocket({
  workspaceId,
  token,
  onMessage,
}: UseCommerceWebSocketOptions) {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    if (!token || !workspaceId) return;

    const url = `${WS_BASE}/commerce/ws/${workspaceId}?token=${token}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const message: CommerceWSMessage = JSON.parse(event.data);
        onMessageRef.current?.(message);
      } catch {
        // Ignore malformed messages
      }
    };

    ws.onclose = () => {
      setConnected(false);
      // Auto-reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [token, workspaceId]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      wsRef.current?.close();
    };
  }, [connect]);

  return { connected };
}
