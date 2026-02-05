from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from infograph.core.schemas import ResearchSession, ResearchSessionCreate, ResearchSessionUpdate


class AbstractSessionStore(ABC):
    @abstractmethod
    async def create(self, create: ResearchSessionCreate, user_id: str) -> ResearchSession:
        raise NotImplementedError

    @abstractmethod
    async def get(self, session_id: str) -> ResearchSession | None:
        raise NotImplementedError

    @abstractmethod
    async def list_for_user(self, user_id: str) -> Iterable[ResearchSession]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, session_id: str, update: ResearchSessionUpdate) -> ResearchSession:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, session_id: str) -> None:
        raise NotImplementedError
