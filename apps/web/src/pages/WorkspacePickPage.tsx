import { Building2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Badge,
  Button,
  Card,
  CardContent,
  EmptyState,
  ErrorState,
  LinkButton,
  LoadingState,
  PageHeader,
} from "../components/ui";
import { authHeaders, getApiPrefix } from "../lib/api";
import { cn } from "../lib/cn";

type Row = {
  id: string;
  name: string;
  slug: string;
  organizationId: string;
  role: string;
};

export function WorkspacePickPage() {
  const nav = useNavigate();
  const [rows, setRows] = useState<Row[] | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [, setBump] = useState(0);
  const selectedId = localStorage.getItem("frodo_workspace_id");

  useEffect(() => {
    void (async () => {
      const r = await fetch(`${getApiPrefix()}/api/workspaces`, {
        headers: authHeaders(),
      });
      if (r.status === 401) {
        nav("/login");
        return;
      }
      if (!r.ok) {
        setErr(`Could not load workspaces (HTTP ${r.status}).`);
        return;
      }
      const j = (await r.json()) as { workspaces: Row[] };
      setRows(j.workspaces);
      if (j.workspaces.length === 1) {
        localStorage.setItem("frodo_workspace_id", j.workspaces[0]!.id);
      }
    })();
  }, [nav]);

  function choose(id: string) {
    localStorage.setItem("frodo_workspace_id", id);
    nav("/connect/shop");
  }

  if (err) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Workspace"
          description="Choose the workspace used for TikTok Shop tokens and sync jobs."
        />
        <ErrorState message={err} />
      </div>
    );
  }

  if (!rows) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Workspace"
          description="Choose the workspace used for TikTok Shop tokens and sync jobs."
        />
        <LoadingState message="Loading workspaces…" />
      </div>
    );
  }

  if (rows.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader title="Workspace" description="No workspaces available." />
        <EmptyState
          icon={Building2}
          title="No workspaces"
          description="Your account has no workspace memberships yet. Complete registration or contact an admin."
          action={
            <LinkButton to="/" variant="outline">
              Back to overview
            </LinkButton>
          }
        />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Workspace"
        description="Select the workspace context for Shop Connect and commerce sync. You can switch later from the header."
        actions={
          <LinkButton to="/connect/shop" variant="outline">
            Continue to Connect Shop
          </LinkButton>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2">
        {rows.map((w) => {
          const active = w.id === selectedId;
          return (
            <Card
              key={w.id}
              className={cn(
                "transition-colors",
                active && "border-coral/30 ring-1 ring-coral/50",
              )}
            >
              <CardContent className="flex flex-col gap-4 p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-800">
                      <Building2 className="h-5 w-5 text-coral" />
                    </div>
                    <div>
                      <p className="font-semibold text-white">{w.name}</p>
                      <p className="font-mono text-xs text-zinc-500">{w.slug}</p>
                    </div>
                  </div>
                  {active ? (
                    <Badge className="border-coral/40 bg-coral/10 text-coral">
                      Selected
                    </Badge>
                  ) : (
                    <Badge>Role: {w.role}</Badge>
                  )}
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button
                    type="button"
                    variant="gradient"
                    onClick={() => choose(w.id)}
                  >
                    Use this workspace
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => {
                      localStorage.setItem("frodo_workspace_id", w.id);
                      setBump((b) => b + 1);
                    }}
                  >
                    Set active (stay here)
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
