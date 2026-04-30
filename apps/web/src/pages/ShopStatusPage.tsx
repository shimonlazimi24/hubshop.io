import { ChevronRight, Store } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Button,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from "../components/ui";
import { authHeaders, getApiPrefix } from "../lib/api";

export function ShopStatusPage() {
  const nav = useNavigate();
  const [json, setJson] = useState<unknown>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      const ws = localStorage.getItem("frodo_workspace_id");
      if (!ws) {
        setErr("No workspace selected.");
        return;
      }
      const r = await fetch(`${getApiPrefix()}/api/connect/shop/status`, {
        headers: authHeaders(ws),
      });
      if (r.status === 401) {
        nav("/login");
        return;
      }
      if (!r.ok) {
        setErr(`Could not load status (HTTP ${r.status}).`);
        return;
      }
      setJson(await r.json());
    })();
  }, [nav]);

  if (err) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Shops"
          description="Authorized TikTok Shop storefronts for this workspace."
        />
        <ErrorState message={err} />
        <Link to="/workspace">
          <Button type="button" variant="secondary">
            Pick workspace
          </Button>
        </Link>
      </div>
    );
  }

  if (!json) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Shops"
          description="Authorized TikTok Shop storefronts for this workspace."
        />
        <LoadingState message="Loading shops…" />
      </div>
    );
  }

  const data = json as {
    shops?: Array<{ id: string; shopId?: string; shopName?: string }>;
  };
  const shops = data.shops ?? [];

  return (
    <div className="space-y-8">
      <PageHeader
        title="Shops"
        description="Connection and discovery status for TikTok Shop. Open a shop for product and order sync."
        actions={
          <Link to="/connect/shop">
            <Button type="button">Connect another shop</Button>
          </Link>
        }
      />

      {shops.length === 0 ? (
        <EmptyState
          icon={Store}
          title="No shops connected"
          description="Complete TikTok Shop OAuth for this workspace. After discovery finishes, shops appear here."
          action={
            <Link to="/connect/shop">
              <Button type="button">Connect TikTok Shop</Button>
            </Link>
          }
        />
      ) : (
        <Table>
          <TableHead>
            <TableRow>
              <TableHeaderCell>Shop</TableHeaderCell>
              <TableHeaderCell>TikTok shop ID</TableHeaderCell>
              <TableHeaderCell>Hubshop ID</TableHeaderCell>
              <TableHeaderCell className="w-28 text-right">Open</TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {shops.map((s) => (
              <TableRow key={s.id}>
                <TableCell className="font-medium text-white">
                  {s.shopName ?? "—"}
                </TableCell>
                <TableCell className="font-mono text-xs text-zinc-400">
                  {s.shopId ?? "—"}
                </TableCell>
                <TableCell className="font-mono text-xs text-zinc-500">
                  {s.id}
                </TableCell>
                <TableCell className="text-right">
                  <Link
                    to={`/shops/${s.id}`}
                    onClick={() =>
                      localStorage.setItem("frodo_last_shop_id", s.id)
                    }
                    className="inline-flex items-center gap-1 text-sm font-medium text-coral hover:text-coral-dark"
                  >
                    Detail
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {import.meta.env.DEV ? (
        <details className="rounded-lg border border-zinc-800 bg-zinc-900/40">
          <summary className="cursor-pointer px-4 py-3 text-sm font-medium text-zinc-400">
            Debug: raw API response
          </summary>
          <pre className="max-h-64 overflow-auto border-t border-zinc-800 p-4 font-mono text-xs text-zinc-500">
            {JSON.stringify(json, null, 2)}
          </pre>
        </details>
      ) : null}
    </div>
  );
}
