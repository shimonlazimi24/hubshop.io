import { ExternalLink, ListChecks, Shield } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  ErrorState,
  PageHeader,
} from "../components/ui";
import { authHeaders, getApiPrefix } from "../lib/api";

export function ConnectShopPage() {
  const nav = useNavigate();
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function startOAuth() {
    setMsg(null);
    const ws = localStorage.getItem("frodo_workspace_id");
    if (!ws) {
      setMsg("Pick a workspace first.");
      nav("/workspace");
      return;
    }
    setLoading(true);
    try {
      const r = await fetch(`${getApiPrefix()}/api/connect/shop/authorize`, {
        headers: authHeaders(ws),
      });
      if (r.status === 401) {
        nav("/login");
        return;
      }
      if (!r.ok) {
        const j = (await r.json().catch(() => ({}))) as { message?: string };
        setMsg(j.message ?? `HTTP ${r.status}`);
        return;
      }
      const j = (await r.json()) as { authorize_url: string };
      window.location.href = j.authorize_url;
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Connect TikTok Shop"
        description="Authorize Hubshop against your TikTok Shop seller account. Tokens are stored encrypted; discovery runs in the background worker."
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Integration</CardTitle>
            <CardDescription>
              You will leave this app to approve OAuth access in TikTok&apos;s consent screen,
              then return to Hubshop for shop discovery.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex flex-wrap gap-3">
              <Button
                type="button"
                className="gap-2"
                disabled={loading}
                onClick={() => void startOAuth()}
              >
                <ExternalLink className="h-4 w-4" />
                {loading ? "Starting…" : "Start TikTok Shop OAuth"}
              </Button>
              <Link to="/shops">
                <Button type="button" variant="secondary">
                  View shops &amp; status
                </Button>
              </Link>
            </div>

            {msg ? (
              <ErrorState title="Could not start OAuth" message={msg} />
            ) : null}

            <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 p-4">
              <p className="text-sm font-medium text-zinc-200">Before you begin</p>
              <ul className="mt-3 space-y-2 text-sm text-zinc-400">
                <li className="flex gap-2">
                  <Shield className="mt-0.5 h-4 w-4 shrink-0 text-coral" />
                  Signed in with a valid Hubshop session (JWT).
                </li>
                <li className="flex gap-2">
                  <ListChecks className="mt-0.5 h-4 w-4 shrink-0 text-coral" />
                  Workspace selected — credentials are scoped per workspace.
                </li>
                <li className="flex gap-2">
                  <ExternalLink className="mt-0.5 h-4 w-4 shrink-0 text-coral" />
                  TikTok Partner app redirect URI must match your API deployment.
                </li>
              </ul>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Checklist</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-zinc-400">
            <p>
              <span className="font-medium text-zinc-300">API</span> — TikTok app key, secret,
              service ID, and redirect configured.
            </p>
            <p>
              <span className="font-medium text-zinc-300">Worker</span> — SQS queue consuming{" "}
              <code className="rounded bg-zinc-800 px-1 py-0.5 font-mono text-xs">
                shop_discovery_after_connect
              </code>
              .
            </p>
            <p>
              <span className="font-medium text-zinc-300">Encryption</span> — matching{" "}
              <code className="rounded bg-zinc-800 px-1 py-0.5 font-mono text-xs">
                TOKEN_ENCRYPTION_KEY
              </code>{" "}
              on API and worker.
            </p>
            <Link
              to="/workspace"
              className="inline-block text-sm font-medium text-coral hover:text-coral-dark"
            >
              Review workspace →
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
