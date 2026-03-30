import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import (
    PaginatedResponse,
    PaymentResponse,
    SettlementResponse,
    TransactionResponse,
)
from backend.modules.commerce.services.finance_analytics import FinanceAnalyticsService
from backend.modules.commerce.services.finance_service import FinanceService
from backend.modules.commerce.services.shop_service import ShopService

router = APIRouter()


@router.get(
    "/finance/settlements",
    response_model=PaginatedResponse[SettlementResponse],
)
async def list_settlements(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[SettlementResponse]:
    service = FinanceService(db)
    result = await service.list_settlements(
        workspace_id,
        shop_id=shop_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[SettlementResponse.model_validate(s) for s in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get("/finance/settlements/{settlement_id}", response_model=SettlementResponse)
async def get_settlement(
    settlement_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> SettlementResponse:
    service = FinanceService(db)
    settlement = await service.get_settlement(settlement_id)
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Settlement not found"
        )
    return SettlementResponse.model_validate(settlement)


@router.get(
    "/finance/transactions",
    response_model=PaginatedResponse[TransactionResponse],
)
async def list_transactions(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
    transaction_type: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[TransactionResponse]:
    service = FinanceService(db)
    result = await service.list_transactions(
        workspace_id,
        shop_id=shop_id,
        transaction_type=transaction_type,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[TransactionResponse.model_validate(t) for t in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get(
    "/finance/payments",
    response_model=PaginatedResponse[PaymentResponse],
)
async def list_payments(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[PaymentResponse]:
    service = FinanceService(db)
    result = await service.list_payments(
        workspace_id, shop_id=shop_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[PaymentResponse.model_validate(p) for p in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post("/finance/sync")
async def sync_finance(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
) -> dict:
    shop_service = ShopService(db)
    if shop_id:
        shop = await shop_service.get_shop(shop_id)
        if not shop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
            )
        shops = [shop]
    else:
        shops = await shop_service.list_shops(workspace_id)

    service = FinanceService(db)
    total = {"settlements": 0, "transactions": 0, "payments": 0}
    for shop in shops:
        total["settlements"] += await service.sync_settlements(shop)
        total["transactions"] += await service.sync_transactions(shop)
        total["payments"] += await service.sync_payments(shop)

    return {"synced": total}


@router.get("/finance/withdrawals")
async def get_withdrawals(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = FinanceService(db)
    return await service.get_withdrawals(shop_id)


@router.get("/finance/orders/{order_id}/transactions")
async def get_transactions_by_order(
    order_id: str,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = FinanceService(db)
    return await service.get_transactions_by_order(shop_id, order_id)


@router.get("/finance/statements/{statement_id}/transactions")
async def get_transactions_by_statement(
    statement_id: str,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = FinanceService(db)
    return await service.get_transactions_by_statement(shop_id, statement_id)


@router.get("/finance/transactions/unsettled")
async def get_unsettled_transactions(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = FinanceService(db)
    return await service.get_unsettled_transactions(shop_id)


# --- Analytics routes (Phase B4) ---


@router.get("/finance/analytics/revenue-summary")
async def get_revenue_summary(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    period_start: datetime = Query(..., description="Start of period (ISO 8601)"),
    period_end: datetime = Query(..., description="End of period (ISO 8601)"),
) -> dict:
    service = FinanceAnalyticsService(db)
    return await service.get_revenue_summary(
        workspace_id, period_start=period_start, period_end=period_end
    )


@router.get("/finance/analytics/fee-breakdown")
async def get_fee_breakdown(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    period_start: datetime = Query(..., description="Start of period (ISO 8601)"),
    period_end: datetime = Query(..., description="End of period (ISO 8601)"),
) -> list[dict]:
    service = FinanceAnalyticsService(db)
    return await service.get_fee_breakdown(
        workspace_id, period_start=period_start, period_end=period_end
    )
