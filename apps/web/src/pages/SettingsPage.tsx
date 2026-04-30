import { PageHeader } from "../components/ui/PageHeader";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/Card";

export function SettingsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Settings"
        description="Organization profile, billing, and team preferences will appear here as we extend v2."
      />
      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
          <CardDescription>
            Workspace membership and roles are managed from your organization admin flow (coming
            soon).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-zinc-400">
            Use <strong className="text-zinc-300">Switch workspace</strong> in the header to
            change context. Sign out clears local session tokens only.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
