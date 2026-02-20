import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.analytics import Notification, NotificationPreference
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_notifications(
        self,
        user_id: uuid.UUID,
        *,
        workspace_id: uuid.UUID,
        is_read: bool | None = None,
        module: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Notification]:
        query = select(Notification).where(
            Notification.user_id == user_id,
            Notification.workspace_id == workspace_id,
        )
        count_query = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.workspace_id == workspace_id,
        )

        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
            count_query = count_query.where(Notification.is_read == is_read)
        if module:
            query = query.where(Notification.module == module)
            count_query = count_query.where(Notification.module == module)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def create_notification(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        *,
        title: str,
        message: str,
        notification_type: str = "INFO",
        module: str | None = None,
        action_url: str | None = None,
    ) -> Notification:
        notification = Notification(
            workspace_id=workspace_id,
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            module=module,
            action_url=action_url,
        )
        self._session.add(notification)
        await self._session.flush()
        return notification

    async def mark_read(
        self, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> Notification | None:
        result = await self._session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        notification = result.scalar_one_or_none()
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(tz=UTC)
        return notification

    async def mark_all_read(
        self, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> int:
        result = await self._session.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.workspace_id == workspace_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True, read_at=datetime.now(tz=UTC))
        )
        return result.rowcount

    async def get_unread_count(
        self, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> int:
        result = await self._session.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.workspace_id == workspace_id,
                Notification.is_read.is_(False),
            )
        )
        return result.scalar_one()

    async def get_preferences(
        self, user_id: uuid.UUID
    ) -> list[NotificationPreference]:
        result = await self._session.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
        )
        return list(result.scalars().all())

    async def update_preference(
        self,
        user_id: uuid.UUID,
        module: str,
        channel: str,
        is_enabled: bool,
    ) -> NotificationPreference:
        result = await self._session.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id,
                NotificationPreference.module == module,
                NotificationPreference.channel == channel,
            )
        )
        pref = result.scalar_one_or_none()

        if pref:
            pref.is_enabled = is_enabled
        else:
            pref = NotificationPreference(
                user_id=user_id,
                module=module,
                channel=channel,
                is_enabled=is_enabled,
            )
            self._session.add(pref)
            await self._session.flush()

        return pref
