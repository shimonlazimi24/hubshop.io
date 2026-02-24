import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """Extract workspace context from request headers or path params.

    Sets request.state.workspace_id for downstream use.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        workspace_id: str | None = request.headers.get("X-Workspace-Id")
        if workspace_id:
            try:
                request.state.workspace_id = uuid.UUID(workspace_id)
            except ValueError:
                logger.warning("Invalid X-Workspace-Id header: %s", workspace_id)
                request.state.workspace_id = None
        else:
            request.state.workspace_id = None

        return await call_next(request)
