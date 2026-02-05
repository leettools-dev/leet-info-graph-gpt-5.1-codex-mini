from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from infograph.core.schemas import Infographic, InfographicCreate


class AbstractInfographicStore(ABC):
    @abstractmethod
    async def create(self, create: InfographicCreate) -> Infographic:
        raise NotImplementedError

    @abstractmethod
    async def get_for_session(self, session_id: str) -> Infographic | None:
        raise NotImplementedError

    @abstractmethod
    async def list_recent(self, limit: int = 10) -> Iterable[Infographic]:
        raise NotImplementedError
