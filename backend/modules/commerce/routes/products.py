import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import (
    CreateProductRequest,
    EditProductRequest,
    PaginatedResponse,
    PartialEditProductRequest,
    ProductBatchActionRequest,
    ProductDetailResponse,
    ProductSummaryResponse,
    UpdateInventoryRequest,
    UpdatePriceRequest,
    UploadFileRequest,
    UploadImageRequest,
)
from backend.modules.commerce.services.product_service import ProductService
from backend.modules.commerce.services.shop_service import ShopService

router = APIRouter()


@router.get("/products/categories")
async def get_categories(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = ProductService(db)
    return await service.get_categories(shop_id)


@router.post("/products/categories/recommend")
async def recommend_categories(
    shop_id: uuid.UUID,
    product_title: str,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = ProductService(db)
    return await service.recommend_categories(shop_id, product_title)


@router.get("/products/categories/{category_id}/rules")
async def get_category_rules(
    category_id: str,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = ProductService(db)
    return await service.get_category_rules(shop_id, category_id)


@router.get("/products/categories/{category_id}/attributes")
async def get_attributes(
    category_id: str,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = ProductService(db)
    return await service.get_attributes(shop_id, category_id)


@router.post("/products", status_code=201)
async def create_product(
    body: CreateProductRequest,
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ProductService(db)
    return await service.create_product(
        workspace_id,
        uuid.UUID(body.shop_id),
        title=body.title,
        description=body.description,
        category_id=body.category_id,
        images=body.images,
        skus=body.skus,
        package_dimensions=body.package_dimensions,
    )


@router.get(
    "/products",
    response_model=PaginatedResponse[ProductSummaryResponse],
)
async def list_products(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[ProductSummaryResponse]:
    service = ProductService(db)
    result = await service.list_products(
        workspace_id,
        shop_id=shop_id,
        status=status_filter,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[ProductSummaryResponse.model_validate(p) for p in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get(
    "/products/{product_id}",
    response_model=ProductDetailResponse,
)
async def get_product(
    product_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> ProductDetailResponse:
    service = ProductService(db)
    product = await service.get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return ProductDetailResponse.model_validate(product)


@router.post("/products/sync")
async def sync_products(
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shop not found",
            )
        shops = [shop]
    else:
        shops = await shop_service.list_shops(workspace_id)

    product_service = ProductService(db)
    total_synced = 0
    for shop in shops:
        count = await product_service.sync_products(shop)
        total_synced += count

    return {"synced": total_synced}


# --- Task 4: Product Lifecycle Batch Operations ---


@router.post("/products/delete")
async def delete_products(
    body: ProductBatchActionRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ProductService(db)
    return await service.delete_products(uuid.UUID(body.shop_id), body.product_ids)


@router.post("/products/activate")
async def activate_products(
    body: ProductBatchActionRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ProductService(db)
    return await service.activate_products(uuid.UUID(body.shop_id), body.product_ids)


@router.post("/products/deactivate")
async def deactivate_products(
    body: ProductBatchActionRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ProductService(db)
    return await service.deactivate_products(uuid.UUID(body.shop_id), body.product_ids)


@router.post("/products/recover")
async def recover_products(
    body: ProductBatchActionRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ProductService(db)
    return await service.recover_products(uuid.UUID(body.shop_id), body.product_ids)


# --- Task 5: Price & Inventory Update ---


@router.post("/products/prices")
async def update_price(
    body: UpdatePriceRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ProductService(db)
    return await service.update_price_api(
        uuid.UUID(body.shop_id), body.product_id, body.skus
    )


@router.post("/products/inventory")
async def update_inventory_api(
    body: UpdateInventoryRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ProductService(db)
    return await service.update_inventory_api(
        uuid.UUID(body.shop_id), body.product_id, body.skus
    )


# --- Task 6: Image & File Upload ---


@router.post("/products/images/upload")
async def upload_image(
    body: UploadImageRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ProductService(db)
    return await service.upload_product_image(uuid.UUID(body.shop_id), body.image_url)


@router.post("/products/files/upload")
async def upload_file(
    body: UploadFileRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ProductService(db)
    return await service.upload_product_file(
        uuid.UUID(body.shop_id), body.file_url, body.file_name
    )


@router.put("/products/{platform_product_id}")
async def edit_product(
    platform_product_id: str,
    body: EditProductRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ProductService(db)
    return await service.edit_product(
        uuid.UUID(body.shop_id),
        platform_product_id,
        title=body.title,
        description=body.description,
        category_id=body.category_id,
        images=body.images,
        skus=body.skus,
    )


@router.put("/products/{platform_product_id}/partial")
async def partial_edit_product(
    platform_product_id: str,
    body: PartialEditProductRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ProductService(db)
    return await service.partial_edit_product(
        uuid.UUID(body.shop_id),
        platform_product_id,
        title=body.title,
        description=body.description,
        images=body.images,
        skus=body.skus,
    )
