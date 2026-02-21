"use client";

import { useEffect, useState } from "react";
import { DollarSign, CreditCard, Wallet, ArrowUpDown } from "lucide-react";
import { listSettlements, listTransactions, listPayments, type Settlement, type Transaction, type Payment, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { PageShell } from "@/components/ui/page-shell";
import { MetricBar } from "@/components/ui/metric-bar";
import { MetricCard } from "@/components/ui/metric-card";
import { ChartCard } from "@/components/ui/chart-card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { StatusBadge } from "@/components/ui/status-badge";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

type Tab = "settlements" | "transactions" | "payments";

const settlementColumns: Column<Settlement>[] = [
  {
    key: "id",
    header: "Settlement ID",
    render: (row) => <span className="text-sm text-gray-900 font-mono">{row.platform_settlement_id}</span>,
  },
  {
    key: "amount",
    header: "Amount",
    sortable: true,
    render: (row) => <span className="text-sm font-medium text-gray-900 tabular-nums">{row.currency} {row.amount}</span>,
  },
  {
    key: "status",
    header: "Status",
    render: (row) => <StatusBadge variant="completed" label={row.status} />,
  },
  {
    key: "period",
    header: "Period",
    render: (row) => (
      <span className="text-sm text-gray-500">
        {row.period_start ? new Date(row.period_start).toLocaleDateString() : "-"}
        {row.period_end ? ` - ${new Date(row.period_end).toLocaleDateString()}` : ""}
      </span>
    ),
  },
];

const transactionColumns: Column<Transaction>[] = [
  {
    key: "id",
    header: "Transaction ID",
    render: (row) => <span className="text-sm text-gray-900 font-mono">{row.platform_transaction_id}</span>,
  },
  {
    key: "type",
    header: "Type",
    render: (row) => <span className="text-sm text-gray-600">{row.transaction_type}</span>,
  },
  {
    key: "amount",
    header: "Amount",
    sortable: true,
    render: (row) => <span className="text-sm font-medium text-gray-900 tabular-nums">{row.currency} {row.amount}</span>,
  },
  {
    key: "date",
    header: "Date",
    sortable: true,
    render: (row) => <span className="text-sm text-gray-500">{new Date(row.created_at).toLocaleDateString()}</span>,
  },
];

const paymentColumns: Column<Payment>[] = [
  {
    key: "id",
    header: "Payment ID",
    render: (row) => <span className="text-sm text-gray-900 font-mono">{row.platform_payment_id}</span>,
  },
  {
    key: "amount",
    header: "Amount",
    sortable: true,
    render: (row) => <span className="text-sm font-medium text-gray-900 tabular-nums">{row.currency} {row.amount}</span>,
  },
  {
    key: "status",
    header: "Status",
    render: (row) => <StatusBadge variant="completed" label={row.status} />,
  },
  {
    key: "date",
    header: "Date",
    sortable: true,
    render: (row) => <span className="text-sm text-gray-500">{new Date(row.created_at).toLocaleDateString()}</span>,
  },
];

export default function FinancePage() {
  const [tab, setTab] = useState<Tab>("settlements");
  const [settlements, setSettlements] = useState<PaginatedResponse<Settlement> | null>(null);
  const [transactions, setTransactions] = useState<PaginatedResponse<Transaction> | null>(null);
  const [payments, setPayments] = useState<PaginatedResponse<Payment> | null>(null);
  const [loading, setLoading] = useState(true);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    const fetcher =
      tab === "settlements" ? listSettlements(WORKSPACE_ID, token).then(setSettlements) :
      tab === "transactions" ? listTransactions(WORKSPACE_ID, token).then(setTransactions) :
      listPayments(WORKSPACE_ID, token).then(setPayments);
    fetcher.catch(console.error).finally(() => setLoading(false));
  }, [tab]);

  const tabs: { key: Tab; label: string }[] = [
    { key: "settlements", label: "Settlements" },
    { key: "transactions", label: "Transactions" },
    { key: "payments", label: "Payments" },
  ];

  return (
    <PageShell
      header={
        <MetricBar>
          <MetricCard
            label="Total Settled"
            value="$24.8K"
            icon={DollarSign}
            iconColor="text-success"
            trend={{ value: 15.2, direction: "up", label: "vs last month" }}
            sparklineData={[18, 19, 20, 21, 22, 23, 24.8]}
            loading={loading}
          />
          <MetricCard
            label="Pending Payments"
            value="$3.2K"
            icon={Wallet}
            iconColor="text-warning"
            loading={loading}
          />
          <MetricCard
            label="Transactions"
            value={transactions?.total ?? 0}
            icon={ArrowUpDown}
            iconColor="text-info"
            loading={loading}
          />
          <MetricCard
            label="Avg Settlement"
            value="$1.6K"
            icon={CreditCard}
            iconColor="text-purple"
            loading={loading}
          />
        </MetricBar>
      }
    >
      {/* Revenue/settlement chart placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <ChartCard title="Revenue Trend">
          <div className="flex items-end gap-1 h-full px-2">
            {[65, 72, 80, 68, 85, 92, 88].map((v, i) => (
              <div key={i} className="flex-1">
                <div
                  className="bg-success/80 rounded-t hover:bg-success transition-colors"
                  style={{ height: `${v}%` }}
                />
              </div>
            ))}
          </div>
        </ChartCard>
        <ChartCard title="Settlement Timeline">
          <div className="flex items-end gap-1 h-full px-2">
            {[40, 55, 48, 62, 58, 70, 65].map((v, i) => (
              <div key={i} className="flex-1">
                <div
                  className="bg-purple/80 rounded-t hover:bg-purple transition-colors"
                  style={{ height: `${v}%` }}
                />
              </div>
            ))}
          </div>
        </ChartCard>
      </div>

      {/* Tab selector */}
      <div className="flex items-center gap-1 rounded-lg bg-gray-100 p-0.5 w-fit mb-4">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition-all duration-[var(--duration-fast)] ${
              tab === t.key
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Data tables */}
      {tab === "settlements" && (
        <DataTable
          columns={settlementColumns}
          data={settlements?.items ?? []}
          keyExtractor={(row) => row.id}
          emptyTitle="No settlements found"
          loading={loading}
        />
      )}

      {tab === "transactions" && (
        <DataTable
          columns={transactionColumns}
          data={transactions?.items ?? []}
          keyExtractor={(row) => row.id}
          emptyTitle="No transactions found"
          loading={loading}
        />
      )}

      {tab === "payments" && (
        <DataTable
          columns={paymentColumns}
          data={payments?.items ?? []}
          keyExtractor={(row) => row.id}
          emptyTitle="No payments found"
          loading={loading}
        />
      )}
    </PageShell>
  );
}
