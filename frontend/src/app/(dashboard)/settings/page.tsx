export default function SettingsPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Settings</h2>
      <p className="text-gray-500 mb-8">
        Manage your organization, workspaces, team members, and preferences.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-2">Organization</h3>
          <p className="text-sm text-gray-500">
            Manage organization name, billing, and subscription.
          </p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-2">Workspaces</h3>
          <p className="text-sm text-gray-500">
            Create and manage workspaces for different brands or teams.
          </p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-2">Team</h3>
          <p className="text-sm text-gray-500">
            Invite team members and manage roles and permissions.
          </p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-2">Webhooks</h3>
          <p className="text-sm text-gray-500">
            Configure webhook endpoints for real-time event notifications.
          </p>
        </div>
      </div>
    </div>
  );
}
