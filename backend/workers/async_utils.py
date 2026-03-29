"""Shared async utilities for Celery workers.

Provides a decorator to run async functions in Celery tasks without
each task manually creating and closing an event loop.
"""

import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Any


def async_task(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to run async functions in Celery tasks with a per-invocation event loop.

    Usage::

        @celery_app.task(name="backend.workers.example.my_task")
        @async_task
        async def my_task(arg: str) -> None:
            async with async_session_factory() as session:
                ...
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()

    return wrapper
