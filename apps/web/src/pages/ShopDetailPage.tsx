import { ArrowLeft, Package, Receipt, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  Button,
  Card,
  CardContent,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
  StatusBadge,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from "../components/ui";
import { authHeaders, getApiPrefix } from "../lib/api";
import { cn } from "../lib/cn";

type Tab = "products" | "orders";

function syncTone(
  status: string | undefined,
): "success" | "warning" | "danger" | "neutral" {
  const s = (status ?? "").toLowerCase();
  if (s === "completed") {
    return "success";
  }
  if (s === "running") {
    return "warning";
  }
  if (s === "failed") {
    return "danger";
  }
  return "neutral";
}

export function ShopDetailPage() {
  const { shopId } = useParams<{ shopId: string }>();
  const nav = useNavigate();
  const [tab, setTab] = useState<Tab>("products");
  const [syncStatus, setSyncStatus] = useState<unknown>(null);
  const [products, setProducts] = useState<unknown[]>([]);
  const [orders, setOrders] = useState<unknown[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [pageLoading, setPageLoading] = useState(true);

  const ws = localStorage.getItem("frodo_workspace_id");
  const prefix = getApiPrefix();

  useEffect(() => {
    if (shopId) {
      localStorage.setItem("frodo_last_shop_id", shopId);
    }
  }, [shopId]);

  const loadAll = useCallback(async () => {
    if (!shopId || !ws) {
      setPageLoading(false);
      return;
    }
    setErr(null);
    setPageLoading(true);
    const h = authHeaders(ws);

    const [st, pr, ord] = await Promise.all([
      fetch(`${prefix}/api/commerce/shops/${shopId}/sync-status`, {
        headers: h,
      }),
      fetch(`${prefix}/api/commerce/shops/${shopId}/products`, {
        headers: h,
      }),
      fetch(`${prefix}/api/commerce/shops/${shopId}/orders`, {
        headers: h,
      }),
    ]);

    if (st.status === 401 || pr.status === 401 || ord.status === 401) {
      nav("/login");
      setPageLoading(false);
      return;
    }

    if (!st.ok) {
      setErr(`Sync status failed (HTTP ${st.status}).`);
      setPageLoading(false);
      return;
    }
    if (!pr.ok) {
      setErr(`Products failed (HTTP ${pr.status}).`);
      setPageLoading(false);
      return;
    }
    if (!ord.ok) {
      setErr(`Orders failed (HTTP ${ord.status}).`);
      setPageLoading(false);
      return;
    }

    const sj = await st.json();
    const pj = await pr.json();
    const oj = await ord.json();
    setSyncStatus(sj);
    setProducts((pj as { products?: unknown[] }).products ?? []);
    setOrders((oj as { orders?: unknown[] }).orders ?? []);
    setPageLoading(false);
  }, [nav, prefix, shopId, ws]);

  useEffect(() => {
    void loadAll();
  }, [loadAll]);

  async function triggerSync(kind: "products" | "orders") {
    if (!shopId || !ws) {
      return;
    }
    setBusy(kind);
    setErr(null);
    const path =
      kind === "products"
        ? `${prefix}/api/commerce/shops/${shopId}/sync-products`
        : `${prefix}/api/commerce/shops/${shopId}/sync-orders`;
    const r = await fetch(path, {
      method: "POST",
      headers: authHeaders(ws),
    });
    setBusy(null);
    if (r.status === 401) {
      nav("/login");
      return;
    }
    if (!r.ok) {
      let msg = `HTTP ${r.status}`;
      try {
        const b = (await r.json()) as { message?: unknown };
        if (b?.message) {
          msg = Array.isArray(b.message)
            ? String(b.message[0])
            : String(b.message);
        }
      } catch {
        /* ignore */
      }
      setErr(msg);
      return;
    }
    await loadAll();
  }

  if (!ws) {
    return (
      <div className="space-y-6">
        <ErrorState message="No workspace selected." />
        <Link to="/workspace">
          <Button type="button" variant="secondary">
            Pick workspace
          </Button>
        </Link>
      </div>
    );
  }

  if (!shopId) {
    return <ErrorState message="Missing shop id in route." />;
  }

  const ss = syncStatus as {
    shopName?: string;
    latestProductSync?: {
      status: string;
      itemsSynced?: number;
      errorMessage?: string | null;
    } | null;
    latestOrderSync?: {
      status: string;
      itemsSynced?: number;
      errorMessage?: string | null;
    } | null;
  } | null;

  return (
    <div className="space-y-8">
      <PageHeader
        title={ss?.shopName ?? "Shop"}
        description={`Internal shop ID · ${shopId}`}
        actions={
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="secondary"
              className="gap-2"
              disabled={busy !== null || pageLoading}
              onClick={() => void triggerSync("products")}
            >
              <Package className="h-4 w-4" />
              {busy === "products" ? "Syncing…" : "Sync products"}
            </Button>
            <Button
              type="button"
              variant="secondary"
              className="gap-2"
              disabled={busy !== null || pageLoading}
              onClick={() => void triggerSync("orders")}
            >
              <Receipt className="h-4 w-4" />
              {busy === "orders" ? "Syncing…" : "Sync orders"}
            </Button>
            <Button
              type="button"
              variant="ghost"
              className="gap-2"
              disabled={pageLoading}
              onClick={() => void loadAll()}
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
          </div>
        }
      />

      <Link
        to="/shops"
        className="inline-flex items-center gap-2 text-sm font-medium text-zinc-400 hover:text-white"
      >
        <ArrowLeft className="h-4 w-4" />
        All shops
      </Link>

      {pageLoading ? (
        <LoadingState message="Loading shop data…" />
      ) : err ? (
        <ErrorState message={err} onRetry={() => void loadAll()} />
      ) : null}

      {!pageLoading && !err ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            <Card>
              <CardContent className="space-y-3 p-5">
                <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                  Products sync
                </p>
                {ss?.latestProductSync ? (
                  <>
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusBadge tone={syncTone(ss.latestProductSync.status)}>
                        {ss.latestProductSync.status}
                      </StatusBadge>
                      <span className="text-sm text-zinc-400">
                        {ss.latestProductSync.itemsSynced ?? 0} items
                      </span>
                    </div>
                    {ss.latestProductSync.errorMessage ? (
                      <p className="text-sm text-red-300">
                        {ss.latestProductSync.errorMessage}
                      </p>
                    ) : null}
                  </>
                ) : (
                  <p className="text-sm text-zinc-500">No product sync job yet.</p>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardContent className="space-y-3 p-5">
                <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                  Orders sync
                </p>
                {ss?.latestOrderSync ? (
                  <>
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusBadge tone={syncTone(ss.latestOrderSync.status)}>
                        {ss.latestOrderSync.status}
                      </StatusBadge>
                      <span className="text-sm text-zinc-400">
                        {ss.latestOrderSync.itemsSynced ?? 0} items
                      </span>
                    </div>
                    {ss.latestOrderSync.errorMessage ? (
                      <p className="text-sm text-red-300">
                        {ss.latestOrderSync.errorMessage}
                      </p>
                    ) : null}
                  </>
                ) : (
                  <p className="text-sm text-zinc-500">No order sync job yet.</p>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="flex gap-1 rounded-xl border border-zinc-800 bg-zinc-900/50 p-1">
            <button
              type="button"
              className={cn(
                "flex flex-1 items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors",
                tab === "products"
                  ? "bg-zinc-800 text-white shadow-sm"
                  : "text-zinc-400 hover:text-white",
              )}
              onClick={() => setTab("products")}
            >
              <Package className="h-4 w-4" />
              Products ({products.length})
            </button>
            <button
              type="button"
              className={cn(
                "flex flex-1 items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors",
                tab === "orders"
                  ? "bg-zinc-800 text-white shadow-sm"
                  : "text-zinc-400 hover:text-white",
              )}
              onClick={() => setTab("orders")}
            >
              <Receipt className="h-4 w-4" />
              Orders ({orders.length})
            </button>
          </div>

          {tab === "products" ? (
            products.length === 0 ? (
              <EmptyState
                icon={Package}
                title="No products"
                description="Run a product sync after TikTok authorization. Empty catalog can also mean no listings in TikTok."
                action={
                  <Button
                    type="button"
                    disabled={busy !== null}
                    onClick={() => void triggerSync("products")}
                  >
                    Sync products
                  </Button>
                }
              />
            ) : (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableHeaderCell>Title</TableHeaderCell>
                    <TableHeaderCell>Status</TableHeaderCell>
                    <TableHeaderCell>Price</TableHeaderCell>
                    <TableHeaderCell>Snapshot</TableHeaderCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {products.map((p) => {
                    const row = p as Record<string, unknown>;
                    return (
                      <TableRow key={String(row.id)}>
                        <TableCell className="max-w-xs truncate font-medium text-white">
                          {String(row.title ?? "—")}
                        </TableCell>
                        <TableCell>
                          <span className="capitalize text-zinc-300">
                            {String(row.status ?? "—")}
                          </span>
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {row.priceAmount != null
                            ? `${String(row.priceAmount)} ${String(row.currency ?? "")}`
                            : "—"}
                        </TableCell>
                        <TableCell>
                          {row.hasApiSnapshot ? (
                            <StatusBadge tone="success">Stored</StatusBadge>
                          ) : (
                            <span className="text-zinc-500">—</span>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            )
          ) : orders.length === 0 ? (
            <EmptyState
              icon={Receipt}
              title="No orders"
              description="Run an order sync to pull recent TikTok Shop orders for this storefront."
              action={
                <Button
                  type="button"
                  disabled={busy !== null}
                  onClick={() => void triggerSync("orders")}
                >
                  Sync orders
                </Button>
              }
            />
          ) : (
            <Table>
              <TableHead>
                <TableRow>
                  <TableHeaderCell>Order</TableHeaderCell>
                  <TableHeaderCell>Status</TableHeaderCell>
                  <TableHeaderCell>Total</TableHeaderCell>
                  <TableHeaderCell>Snapshot</TableHeaderCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {orders.map((o) => {
                  const row = o as Record<string, unknown>;
                  return (
                    <TableRow key={String(row.id)}>
                      <TableCell className="font-mono text-sm text-white">
                        {String(row.platformOrderId ?? row.id ?? "—")}
                      </TableCell>
                      <TableCell className="capitalize text-zinc-300">
                        {String(row.status ?? "—")}
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {String(row.totalAmount ?? "—")}{" "}
                        {String(row.currency ?? "")}
                      </TableCell>
                      <TableCell>
                        {row.hasApiSnapshot ? (
                          <StatusBadge tone="success">Stored</StatusBadge>
                        ) : (
                          <span className="text-zinc-500">—</span>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </>
      ) : null}
    </div>
  );
}
