import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.automation_service import AutomationService

router = APIRouter()


class CreateRuleRequest(BaseModel):
    ad_account_id: str
    rule_config: dict


class UpdateRuleRequest(BaseModel):
    ad_account_id: str
    updates: dict


class DeleteRuleRequest(BaseModel):
    ad_account_id: str


@router.get("/automation/rules")
async def list_rules(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = AutomationService(db)
    return await service.list_rules(
        workspace_id, ad_account, page=page, page_size=page_size
    )


@router.post("/automation/rules")
async def create_rule(
    workspace_id: uuid.UUID,
    body: CreateRuleRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = AutomationService(db)
    return await service.create_rule(
        workspace_id, ad_account, rule_config=body.rule_config
    )


@router.post("/automation/rules/{rule_id}")
async def update_rule(
    workspace_id: uuid.UUID,
    rule_id: str,
    body: UpdateRuleRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = AutomationService(db)
    return await service.update_rule(
        workspace_id, ad_account, rule_id=rule_id, updates=body.updates
    )


@router.delete("/automation/rules/{rule_id}")
async def delete_rule(
    workspace_id: uuid.UUID,
    rule_id: str,
    body: DeleteRuleRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = AutomationService(db)
    return await service.delete_rule(workspace_id, ad_account, rule_id=rule_id)
