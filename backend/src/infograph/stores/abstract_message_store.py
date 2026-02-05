from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from infograph.core.schemas import Message, MessageCreate


class AbstractMessageStore(ABC):
    @abstractmethod
    async def create(self, create: MessageCreate) -> Message:
        raise NotImplementedError

    @abstractmethod
    async def list_for_session(self, session_id: str) -> Iterable[Message]:
        raise NotImplementedError

    @abstractmethod
    async def delete_for_session(self, session_id: str) -> None:
        raise NotImplementedError
