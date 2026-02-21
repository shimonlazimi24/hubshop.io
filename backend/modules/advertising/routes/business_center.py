import uuid

from fastapi import APIRouter, HTTPException, Query, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.schemas import (
    AddPartnerRequest,
    AssignAssetRequest,
    CreateBCAdAccountRequest,
    InviteMemberRequest,
    UpdateMemberRequest,
)
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.business_center_service import (
    BusinessCenterService,
)

router = APIRouter()


@router.get("/bc")
async def list_business_centers(
    workspace_id: uuid.UUID,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = BusinessCenterService(db)
    return await service.list_business_centers(
        ad_account, page=page, page_size=page_size
    )


@router.get("/bc/{bc_id}/activity-log")
async def get_activity_log(
    workspace_id: uuid.UUID,
    bc_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = BusinessCenterService(db)
    return await service.get_activity_log(
        ad_account, bc_id=bc_id, page=page, page_size=page_size
    )


@router.get("/bc/{bc_id}/members")
async def list_members(
    workspace_id: uuid.UUID,
    bc_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = BusinessCenterService(db)
    return await service.list_members(
        ad_account, bc_id=bc_id, page=page, page_size=page_size
    )


@router.post("/bc/{bc_id}/members/invite")
async def invite_member(
    workspace_id: uuid.UUID,
    bc_id: str,
    body: InviteMemberRequest,
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

    service = BusinessCenterService(db)
    return await service.invite_member(
        ad_account, bc_id=bc_id, emails=body.emails, role=body.role
    )


@router.put("/bc/{bc_id}/members/{member_id}")
async def update_member(
    workspace_id: uuid.UUID,
    bc_id: str,
    member_id: str,
    body: UpdateMemberRequest,
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

    service = BusinessCenterService(db)
    return await service.update_member(
        ad_account, bc_id=bc_id, member_id=member_id, role=body.role
    )


@router.delete("/bc/{bc_id}/members/{member_id}")
async def delete_member(
    workspace_id: uuid.UUID,
    bc_id: str,
    member_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = BusinessCenterService(db)
    return await service.delete_member(
        ad_account, bc_id=bc_id, member_id=member_id
    )


# --- Partner Management ---


@router.get("/bc/{bc_id}/partners")
async def list_partners(
    workspace_id: uuid.UUID,
    bc_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = BusinessCenterService(db)
    return await service.list_partners(
        ad_account, bc_id=bc_id, page=page, page_size=page_size
    )


@router.post("/bc/{bc_id}/partners")
async def add_partner(
    workspace_id: uuid.UUID,
    bc_id: str,
    body: AddPartnerRequest,
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

    service = BusinessCenterService(db)
    return await service.add_partner(
        ad_account,
        bc_id=bc_id,
        partner_bc_id=body.partner_bc_id,
        relationship_type=body.relationship_type,
    )


@router.delete("/bc/{bc_id}/partners/{partner_bc_id}")
async def delete_partner(
    workspace_id: uuid.UUID,
    bc_id: str,
    partner_bc_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = BusinessCenterService(db)
    return await service.delete_partner(
        ad_account, bc_id=bc_id, partner_bc_id=partner_bc_id
    )


# --- Asset Management ---


@router.get("/bc/{bc_id}/assets")
async def list_assets(
    workspace_id: uuid.UUID,
    bc_id: str,
    ad_account_id: str,
    current_user: CurrentUser,
    db: DBSession,
    asset_type: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = BusinessCenterService(db)
    return await service.list_assets(
        ad_account,
        bc_id=bc_id,
        asset_type=asset_type,
        page=page,
        page_size=page_size,
    )


@router.post("/bc/{bc_id}/assets/assign")
async def assign_asset(
    workspace_id: uuid.UUID,
    bc_id: str,
    body: AssignAssetRequest,
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

    service = BusinessCenterService(db)
    return await service.assign_asset(
        ad_account,
        bc_id=bc_id,
        asset_ids=body.asset_ids,
        member_ids=body.member_ids,
    )


@router.post("/bc/{bc_id}/assets/unassign")
async def unassign_asset(
    workspace_id: uuid.UUID,
    bc_id: str,
    body: AssignAssetRequest,
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

    service = BusinessCenterService(db)
    return await service.unassign_asset(
        ad_account,
        bc_id=bc_id,
        asset_ids=body.asset_ids,
        member_ids=body.member_ids,
    )


@router.post("/bc/{bc_id}/ad-accounts")
async def create_ad_account_in_bc(
    workspace_id: uuid.UUID,
    bc_id: str,
    body: CreateBCAdAccountRequest,
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

    service = BusinessCenterService(db)
    return await service.create_ad_account_in_bc(
        ad_account,
        bc_id=bc_id,
        advertiser_name=body.advertiser_name,
        timezone=body.timezone,
        currency=body.currency,
        industry_id=body.industry_id,
    )
