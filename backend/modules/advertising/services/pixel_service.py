import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount, Pixel
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class PixelService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_pixels(
        self,
        workspace_id: uuid.UUID,
        *,
        ad_account_id: uuid.UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Pixel]:
        query = select(Pixel).where(Pixel.workspace_id == workspace_id)
        count_query = select(func.count(Pixel.id)).where(
            Pixel.workspace_id == workspace_id
        )

        if ad_account_id:
            query = query.where(Pixel.ad_account_id == ad_account_id)
            count_query = count_query.where(Pixel.ad_account_id == ad_account_id)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Pixel.updated_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def get_pixel(self, pixel_id: uuid.UUID) -> Pixel | None:
        result = await self._session.execute(
            select(Pixel).where(Pixel.id == pixel_id)
        )
        return result.scalar_one_or_none()

    async def create_pixel(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        name: str,
    ) -> Pixel:
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        resp = await gateway.post(
            "/pixel/create/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "pixel_name": name,
            },
        )
        data = resp.get("data", {})
        platform_id = str(data.get("pixel_id", ""))
        pixel_code = data.get("pixel_code", "")

        pixel = Pixel(
            workspace_id=workspace_id,
            ad_account_id=ad_account.id,
            platform_pixel_id=platform_id,
            name=name,
            pixel_code=pixel_code,
            detail_json=data,
        )
        self._session.add(pixel)
        await self._session.flush()
        return pixel

    async def get_pixel_code(
        self, pixel: Pixel, ad_account: AdAccount
    ) -> str:
        """Fetch the pixel code snippet from TikTok API."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        resp = await gateway.get(
            "/pixel/code/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "pixel_id": pixel.platform_pixel_id,
            },
        )
        code = resp.get("data", {}).get("pixel_code", "")
        pixel.pixel_code = code
        return code

    async def sync_pixels(self, ad_account: AdAccount) -> int:
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)
        synced = 0
        page = 1

        while True:
            resp = await gateway.get(
                "/pixel/list/",
                params={
                    "advertiser_id": ad_account.advertiser_id,
                    "page": str(page),
                    "page_size": "100",
                },
            )
            data = resp.get("data", {})
            pixel_list = data.get("pixels", [])

            for pixel_data in pixel_list:
                await self._upsert_pixel(ad_account, pixel_data)
                synced += 1

            total_page = data.get("page_info", {}).get("total_page", 1)
            if page >= total_page or not pixel_list:
                break
            page += 1

        return synced

    async def _upsert_pixel(
        self, ad_account: AdAccount, pixel_data: dict
    ) -> Pixel:
        platform_id = str(pixel_data.get("pixel_id", ""))
        result = await self._session.execute(
            select(Pixel).where(Pixel.platform_pixel_id == platform_id)
        )
        pixel = result.scalar_one_or_none()

        name = pixel_data.get("pixel_name", "")
        pixel_code = pixel_data.get("pixel_code", "")

        if pixel:
            pixel.name = name
            pixel.pixel_code = pixel_code
            pixel.detail_json = pixel_data
        else:
            pixel = Pixel(
                workspace_id=ad_account.workspace_id,
                ad_account_id=ad_account.id,
                platform_pixel_id=platform_id,
                name=name,
                pixel_code=pixel_code,
                detail_json=pixel_data,
            )
            self._session.add(pixel)
            await self._session.flush()

        return pixel
