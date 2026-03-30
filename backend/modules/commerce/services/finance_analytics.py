"""Finance analytics service — revenue summaries and fee breakdowns."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.finance import Settlement, Transaction


class FinanceAnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_revenue_summary(
        self,
        workspace_id: uuid.UUID,
        *,
        period_start: datetime,
        period_end: datetime,
    ) -> dict:
        """Aggregate payout totals, transaction count, and transaction amounts."""
        # 1. Settlement payouts in period
        settlement_query = select(
            Settlement.payout_amount,
            Settlement.currency,
        ).where(
            Settlement.workspace_id == workspace_id,
            Settlement.period_start >= period_start,
            Settlement.period_end <= period_end,
        )
        settlement_rows = (await self._session.execute(settlement_query)).all()

        total_payout = Decimal("0.00")
        for row in settlement_rows:
            if row.payout_amount:
                total_payout += Decimal(row.payout_amount)

        # 2. Transaction count in period
        txn_count_query = select(func.count(Transaction.id)).where(
            Transaction.workspace_id == workspace_id,
            Transaction.created_at >= period_start,
            Transaction.created_at <= period_end,
        )
        total_transactions = (await self._session.execute(txn_count_query)).scalar_one()

        # 3. Transaction amounts in period
        txn_amounts_query = select(Transaction.amount).where(
            Transaction.workspace_id == workspace_id,
            Transaction.created_at >= period_start,
            Transaction.created_at <= period_end,
        )
        txn_rows = (await self._session.execute(txn_amounts_query)).all()

        total_txn_amount = Decimal("0.00")
        for (amount,) in txn_rows:
            total_txn_amount += Decimal(amount)

        return {
            "total_payout": str(total_payout.quantize(Decimal("0.01"))),
            "total_transactions": total_transactions,
            "total_transaction_amount": str(total_txn_amount.quantize(Decimal("0.01"))),
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
        }

    async def get_fee_breakdown(
        self,
        workspace_id: uuid.UUID,
        *,
        period_start: datetime,
        period_end: datetime,
    ) -> list[dict]:
        """Group transactions by type with totals and counts."""
        query = (
            select(
                Transaction.transaction_type,
                func.sum(cast(Transaction.amount, String)).label("total"),
                func.count(Transaction.id).label("count"),
            )
            .where(
                Transaction.workspace_id == workspace_id,
                Transaction.created_at >= period_start,
                Transaction.created_at <= period_end,
            )
            .group_by(Transaction.transaction_type)
            .order_by(func.count(Transaction.id).desc())
        )
        rows = (await self._session.execute(query)).all()
        return [
            {
                "transaction_type": row.transaction_type,
                "total": row.total,
                "count": row.count,
            }
            for row in rows
        ]
