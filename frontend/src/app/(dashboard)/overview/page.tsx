export default function OverviewPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Overview</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[
          { label: "Connected Accounts", value: "0", color: "blue" },
          { label: "Total Orders", value: "0", color: "green" },
          { label: "Active Campaigns", value: "0", color: "purple" },
          { label: "Total Videos", value: "0", color: "orange" },
        ].map((kpi) => (
          <div key={kpi.label} className="bg-white rounded-lg border border-gray-200 p-6">
            <p className="text-sm text-gray-500">{kpi.label}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{kpi.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Getting Started</h3>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-md">
            <span className="text-blue-600 font-medium">1.</span>
            <span className="text-sm text-gray-700">
              Connect your TikTok Shop account to start managing commerce
            </span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-md">
            <span className="text-gray-400 font-medium">2.</span>
            <span className="text-sm text-gray-500">
              Connect TikTok Ads to monitor your campaigns
            </span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-md">
            <span className="text-gray-400 font-medium">3.</span>
            <span className="text-sm text-gray-500">
              Link your Developer account for content management
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
