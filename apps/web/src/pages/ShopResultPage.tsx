import { CheckCircle2, Link2 } from "lucide-react";
import { Link, useSearchParams } from "react-router-dom";
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  PageHeader,
  StatusBadge,
} from "../components/ui";

const ERROR_HINTS: Record<string, string> = {
  missing_params:
    "The OAuth callback was missing code or state. Start connect again from the app.",
  tiktok_state_invalid:
    "OAuth state expired or invalid. Try connecting again; ensure your clock is correct.",
  tiktok_token_exchange_failed:
    "TikTok rejected the token exchange. Check app credentials and auth code validity.",
  tiktok_token_missing_seller_identity:
    "TikTok did not return a seller identity in the token response. Contact support if this persists.",
  sqs_enqueue_failed:
    "Background jobs could not be queued. The connection was rolled back; retry after infra is healthy.",
  vault_decrypt_failed:
    "Worker could not decrypt stored tokens. Ensure TOKEN_ENCRYPTION_KEY matches the API.",
  tiktok_shop_discovery_failed:
    "Shop discovery failed after connect. Check worker logs and TikTok API signing.",
};

export function ShopResultPage() {
  const [params] = useSearchParams();
  const status = params.get("status");
  const errorCode = params.get("error");
  const decoded = errorCode ? decodeURIComponent(errorCode) : "";
  const hint = decoded ? ERROR_HINTS[decoded] : undefined;

  const ok = status === "connected";

  return (
    <div className="space-y-8">
      <PageHeader
        title="TikTok Shop connection"
        description="OAuth callback result. Discovery runs asynchronously via the worker queue."
      />

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {ok ? (
              <>
                <CheckCircle2 className="h-6 w-6 text-emerald-400" />
                Connected
              </>
            ) : decoded ? (
              <>
                <StatusBadge tone="danger">Error</StatusBadge>
                Connection issue
              </>
            ) : (
              "Result"
            )}
          </CardTitle>
          <CardDescription>
            {ok
              ? "OAuth completed. Authorized shops will appear after discovery finishes."
              : decoded
                ? "Review the code below and retry Connect Shop if needed."
                : "Open this page after returning from TikTok OAuth."}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {ok ? (
            <div className="rounded-lg border border-emerald-500/30 bg-emerald-950/20 px-4 py-3 text-sm text-emerald-100">
              Background job enqueued for shop discovery. Monitor progress under{" "}
              <strong>Shops</strong>.
            </div>
          ) : null}

          {decoded ? (
            <div className="space-y-3 rounded-lg border border-red-500/30 bg-red-950/20 px-4 py-3">
              <p className="font-mono text-sm text-red-200">{decoded}</p>
              {hint ? <p className="text-sm text-red-100/90">{hint}</p> : null}
            </div>
          ) : null}

          {!status && !decoded ? (
            <p className="text-sm text-zinc-400">
              No query parameters present — this screen is shown after TikTok redirects back to
              Hubshop.
            </p>
          ) : null}

          <div className="flex flex-wrap gap-3">
            <Link to="/shops">
              <Button type="button" className="gap-2">
                <Link2 className="h-4 w-4" />
                View shops
              </Button>
            </Link>
            <Link to="/">
              <Button type="button" variant="secondary">
                Overview
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
