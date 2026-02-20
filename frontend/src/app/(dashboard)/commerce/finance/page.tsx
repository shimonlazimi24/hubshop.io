"use client";

import { useEffect, useState } from "react";
import { listSettlements, listTransactions, listPayments, type Settlement, type Transaction, type Payment, type PaginatedResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

const WORKSPACE_ID = "00000000-0000-0000-0000-000000000000";

type Tab = "settlements" | "transactions" | "payments";

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
    <div>
      <div className="flex gap-2 mb-4">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-3 py-1.5 text-sm rounded-md ${tab === t.key ? "bg-gray-900 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        {tab === "settlements" && (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 text-left">
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Settlement ID</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Period</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {settlements?.items.map(s => (
                <tr key={s.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900 font-mono">{s.platform_settlement_id}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">{s.currency} {s.amount}</td>
                  <td className="px-4 py-3"><span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">{s.status}</span></td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {s.period_start ? new Date(s.period_start).toLocaleDateString() : "-"}
                    {s.period_end ? ` - ${new Date(s.period_end).toLocaleDateString()}` : ""}
                  </td>
                </tr>
              ))}
              {!loading && (!settlements || settlements.items.length === 0) && (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">No settlements found</td></tr>
              )}
            </tbody>
          </table>
        )}

        {tab === "transactions" && (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 text-left">
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Transaction ID</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {transactions?.items.map(t => (
                <tr key={t.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900 font-mono">{t.platform_transaction_id}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{t.transaction_type}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">{t.currency} {t.amount}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{new Date(t.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
              {!loading && (!transactions || transactions.items.length === 0) && (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">No transactions found</td></tr>
              )}
            </tbody>
          </table>
        )}

        {tab === "payments" && (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 text-left">
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Payment ID</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {payments?.items.map(p => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900 font-mono">{p.platform_payment_id}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">{p.currency} {p.amount}</td>
                  <td className="px-4 py-3"><span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">{p.status}</span></td>
                  <td className="px-4 py-3 text-sm text-gray-500">{new Date(p.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
              {!loading && (!payments || payments.items.length === 0) && (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">No payments found</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Loading...</div>}
    </div>
  );
}
