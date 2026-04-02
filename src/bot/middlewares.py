"""Middleware for access control."""

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message


class AdminOnlyMiddleware(BaseMiddleware):
    def __init__(self, admin_id: int) -> None:
        self._admin_id = admin_id

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id if event.from_user else None
        if user_id != self._admin_id:
            return
        return await handler(event, data)
