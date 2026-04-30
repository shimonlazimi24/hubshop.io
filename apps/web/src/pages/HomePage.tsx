import { Link2, PlugZap, RefreshCw, ShieldCheck, Store } from "lucide-react";
import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  EmptyState,
  LinkButton,
  MetricCard,
  PageHeader,
} from "../components/ui";
import { authHeaders, getApiPrefix } from "../lib/api";

type HealthState = "loading" | "ok" | "down";

export function HomePage() {
  const apiBase = getApiPrefix();
  const [health, setHealth] = useState<HealthState>("loading");
  const [workspaceName, setWorkspaceName] = useState<string | null>(null);
  const [shopCount, setShopCount] = useState<number | null>(null);
  const [syncHint, setSyncHint] = useState<string | null>(null);
  const [loadingDash, setLoadingDash] = useState(false);

  const token = localStorage.getItem("frodo_access_token");
  const wsId = localStorage.getItem("frodo_workspace_id");

  useEffect(() => {
    void fetch(`${apiBase}/api/health`)
      .then((r) => r.json())
      .then((j: { ok?: boolean }) => setHealth(j.ok ? "ok" : "down"))
      .catch(() => setHealth("down"));
  }, [apiBase]);

  useEffect(() => {
    if (!token || !wsId) {
      setWorkspaceName(null);
      setShopCount(null);
      setSyncHint(null);
      return;
    }
    setLoadingDash(true);
    void (async () => {
      const [wsRes, shopRes] = await Promise.all([
        fetch(`${apiBase}/api/workspaces`, { headers: authHeaders() }),
        fetch(`${apiBase}/api/connect/shop/status`, {
          headers: authHeaders(wsId),
        }),
      ]);

      if (wsRes.ok) {
        const j = (await wsRes.json()) as {
          workspaces: Array<{ id: string; name: string }>;
        };
        const w = j.workspaces.find((x) => x.id === wsId);
        setWorkspaceName(w?.name ?? null);
      } else {
        setWorkspaceName(null);
      }

      if (shopRes.ok) {
        const j = (await shopRes.json()) as {
          shops?: Array<{ id: string; shopName?: string }>;
        };
        const n = j.shops?.length ?? 0;
        setShopCount(n);
        setSyncHint(
          n === 0
            ? "Connect TikTok Shop to discover storefronts."
            : `${n} shop${n === 1 ? "" : "s"} linked — open Sync status or a shop for product sync.`,
        );
      } else {
        setShopCount(null);
        setSyncHint("Could not load shop status.");
      }
      setLoadingDash(false);
    })();
  }, [apiBase, token, wsId]);

  return (
    <div className="space-y-8">
      <PageHeader
        title="Overview"
        description="Monitor connectivity, workspace context, and TikTok Shop linkage. Use quick actions to continue onboarding."
        actions={
          <div className="flex flex-wrap gap-2">
            <LinkButton to="/connect/shop" variant="gradient" className="gap-2">
              <Link2 className="h-4 w-4" />
              Connect Shop
            </LinkButton>
            <LinkButton to="/shops" variant="outline" className="gap-2">
              <Store className="h-4 w-4" />
              View shops
            </LinkButton>
          </div>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="API status"
          value={
            health === "loading"
              ? "…"
              : health === "ok"
                ? "Operational"
                : "Unreachable"
          }
          icon={ShieldCheck}
          iconColor="text-cyan"
          loading={health === "loading"}
          delay={0}
        />

        <MetricCard
          label="Workspace"
          value={
            !token || !wsId
              ? "—"
              : loadingDash
                ? "…"
                : workspaceName ?? "Workspace"
          }
          icon={PlugZap}
          iconColor="text-purple"
          loading={Boolean(token && wsId && loadingDash)}
          delay={0.05}
        />

        <MetricCard
          label="Connected shops"
          value={
            !token || !wsId ? "—" : loadingDash ? "…" : (shopCount ?? "—")
          }
          icon={Store}
          iconColor="text-coral"
          loading={Boolean(token && wsId && loadingDash)}
          delay={0.1}
        />

        <MetricCard
          label="Sync"
          value={shopCount === 0 ? "Start" : "Ready"}
          icon={RefreshCw}
          iconColor="text-success"
          trend={
            shopCount !== null && shopCount > 0
              ? { value: 0, direction: "flat" as const, label: "Commerce live" }
              : undefined
          }
          loading={Boolean(token && wsId && loadingDash)}
          delay={0.15}
        />
      </div>

      {syncHint && token && wsId && !loadingDash ? (
        <p className="text-sm text-zinc-500">{syncHint}</p>
      ) : null}

      {!wsId ? (
        <EmptyState
          icon={Store}
          title="Select a workspace"
          description="Workspace scope drives TikTok Shop tokens and commerce sync jobs."
          action={
            <LinkButton to="/workspace" variant="gradient">
              Choose workspace
            </LinkButton>
          }
        />
      ) : shopCount === 0 && !loadingDash ? (
        <Card>
          <CardHeader>
            <CardTitle>No shops connected yet</CardTitle>
            <CardDescription>
              Finish TikTok Shop authorization for this workspace to discover
              seller storefronts.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <LinkButton to="/connect/shop" variant="gradient" className="gap-2">
              <Link2 className="h-4 w-4" />
              Connect TikTok Shop
            </LinkButton>
            <LinkButton to="/shops" variant="outline">
              View connection status
            </LinkButton>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
