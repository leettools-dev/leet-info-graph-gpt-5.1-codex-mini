from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from infograph.core.schemas import User, UserCreate


class AbstractUserStore(ABC):
    @abstractmethod
    async def create(self, create: UserCreate) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_google_id(self, google_id: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def list(self) -> Iterable[User]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: str) -> None:
        raise NotImplementedError
