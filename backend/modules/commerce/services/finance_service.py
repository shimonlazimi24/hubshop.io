import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import Shop
from backend.db.models.finance import Payment, Settlement, Transaction
from backend.modules.commerce.services.shop_service import ShopService
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class FinanceService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # --- Settlements ---

    async def list_settlements(
        self,
        workspace_id: uuid.UUID,
        *,
        shop_id: uuid.UUID | None = None,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Settlement]:
        query = select(Settlement).where(
            Settlement.workspace_id == workspace_id
        )
        count_query = select(func.count(Settlement.id)).where(
            Settlement.workspace_id == workspace_id
        )

        if shop_id:
            query = query.where(Settlement.shop_id == shop_id)
            count_query = count_query.where(Settlement.shop_id == shop_id)
        if status_filter:
            query = query.where(Settlement.status == status_filter)
            count_query = count_query.where(Settlement.status == status_filter)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Settlement.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def get_settlement(
        self, settlement_id: uuid.UUID
    ) -> Settlement | None:
        result = await self._session.execute(
            select(Settlement).where(Settlement.id == settlement_id)
        )
        return result.scalar_one_or_none()

    async def sync_settlements(self, shop: Shop) -> int:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        synced = 0

        resp = await gateway.get(
            "/finance/202309/settlements",
            params={"page_size": "50"},
        )
        data = resp.get("data", {})
        settlements = data.get("settlements", [])

        for settlement_data in settlements:
            await self._upsert_settlement(shop, settlement_data)
            synced += 1

        return synced

    async def _upsert_settlement(
        self, shop: Shop, data: dict
    ) -> Settlement:
        platform_id = str(data.get("settlement_id", ""))
        result = await self._session.execute(
            select(Settlement).where(
                Settlement.platform_settlement_id == platform_id
            )
        )
        settlement = result.scalar_one_or_none()

        if settlement:
            settlement.amount = str(data.get("amount", "0"))
            settlement.status = data.get("status", "")
            settlement.detail_json = data
        else:
            settlement = Settlement(
                workspace_id=shop.workspace_id,
                shop_id=shop.id,
                platform_settlement_id=platform_id,
                amount=str(data.get("amount", "0")),
                currency=data.get("currency", "USD"),
                status=data.get("status", ""),
                detail_json=data,
            )
            self._session.add(settlement)
            await self._session.flush()

        return settlement

    # --- Transactions ---

    async def list_transactions(
        self,
        workspace_id: uuid.UUID,
        *,
        shop_id: uuid.UUID | None = None,
        transaction_type: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Transaction]:
        query = select(Transaction).where(
            Transaction.workspace_id == workspace_id
        )
        count_query = select(func.count(Transaction.id)).where(
            Transaction.workspace_id == workspace_id
        )

        if shop_id:
            query = query.where(Transaction.shop_id == shop_id)
            count_query = count_query.where(Transaction.shop_id == shop_id)
        if transaction_type:
            query = query.where(Transaction.transaction_type == transaction_type)
            count_query = count_query.where(
                Transaction.transaction_type == transaction_type
            )

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Transaction.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def sync_transactions(self, shop: Shop) -> int:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        synced = 0

        resp = await gateway.get(
            "/finance/202309/transactions",
            params={"page_size": "50"},
        )
        data = resp.get("data", {})
        transactions = data.get("transactions", [])

        for txn_data in transactions:
            await self._upsert_transaction(shop, txn_data)
            synced += 1

        return synced

    async def _upsert_transaction(
        self, shop: Shop, data: dict
    ) -> Transaction:
        platform_id = str(data.get("transaction_id", ""))
        result = await self._session.execute(
            select(Transaction).where(
                Transaction.platform_transaction_id == platform_id
            )
        )
        txn = result.scalar_one_or_none()

        if txn:
            txn.amount = str(data.get("amount", "0"))
            txn.detail_json = data
        else:
            txn = Transaction(
                workspace_id=shop.workspace_id,
                shop_id=shop.id,
                platform_transaction_id=platform_id,
                transaction_type=data.get("type", ""),
                amount=str(data.get("amount", "0")),
                currency=data.get("currency", "USD"),
                order_id=data.get("order_id"),
                detail_json=data,
            )
            self._session.add(txn)
            await self._session.flush()

        return txn

    # --- Payments ---

    async def list_payments(
        self,
        workspace_id: uuid.UUID,
        *,
        shop_id: uuid.UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Payment]:
        query = select(Payment).where(Payment.workspace_id == workspace_id)
        count_query = select(func.count(Payment.id)).where(
            Payment.workspace_id == workspace_id
        )

        if shop_id:
            query = query.where(Payment.shop_id == shop_id)
            count_query = count_query.where(Payment.shop_id == shop_id)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Payment.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def sync_payments(self, shop: Shop) -> int:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        synced = 0

        resp = await gateway.get(
            "/finance/202309/payments",
            params={"page_size": "50"},
        )
        data = resp.get("data", {})
        payments = data.get("payments", [])

        for pmt_data in payments:
            await self._upsert_payment(shop, pmt_data)
            synced += 1

        return synced

    async def _upsert_payment(self, shop: Shop, data: dict) -> Payment:
        platform_id = str(data.get("payment_id", ""))
        result = await self._session.execute(
            select(Payment).where(Payment.platform_payment_id == platform_id)
        )
        pmt = result.scalar_one_or_none()

        if pmt:
            pmt.amount = str(data.get("amount", "0"))
            pmt.status = data.get("status", "")
            pmt.detail_json = data
        else:
            pmt = Payment(
                workspace_id=shop.workspace_id,
                shop_id=shop.id,
                platform_payment_id=platform_id,
                amount=str(data.get("amount", "0")),
                currency=data.get("currency", "USD"),
                status=data.get("status", ""),
                detail_json=data,
            )
            self._session.add(pmt)
            await self._session.flush()

        return pmt
