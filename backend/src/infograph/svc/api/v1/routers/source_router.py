from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from fastapi.routing import APIRoute
from pydantic import BaseModel

from infograph.core.schemas import Source, User
from infograph.services.auth_service import AuthService
from infograph.stores.abstract_session_store import AbstractSessionStore
from infograph.stores.abstract_source_store import AbstractSourceStore
from infograph.stores.abstract_user_store import AbstractUserStore
from infograph.stores.duckdb.session_store_duckdb import SessionStoreDuckDB
from infograph.stores.duckdb.source_store_duckdb import SourceStoreDuckDB
from infograph.stores.duckdb.user_store_duckdb import UserStoreDuckDB
from infograph.svc.api_router_base import APIRouterBase


class SourceRouterResponse(BaseModel):
    sources: list[Source]


class SourceRouter(APIRouterBase):
    def __init__(
        self,
        *,
        session_store: AbstractSessionStore | None = None,
        source_store: AbstractSourceStore | None = None,
        auth_service: AuthService | None = None,
        user_store: AbstractUserStore | None = None,
    ) -> None:
        super().__init__()
        self.session_store = session_store or SessionStoreDuckDB()
        self.source_store = source_store or SourceStoreDuckDB(self.session_store.store.settings)
        self.user_store = user_store or UserStoreDuckDB(self.session_store.store.settings)
        self.auth_service = auth_service or AuthService(self.user_store)
        self._register_routes()

    @staticmethod
    def _extract_token(authorization: str | None) -> str:
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        parts = authorization.strip().split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid Authorization header")

        return parts[1]

    async def _get_current_user(
        self,
        authorization: str | None = Header(None, alias="Authorization"),
    ) -> User:
        token = self._extract_token(authorization)
        try:
            return await self.auth_service.get_user_from_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    def _register_routes(self) -> None:
        @self.get("/{session_id}/sources", response_model=list[Source])
        async def list_sources(
            session_id: str,
            current_user: User = Depends(self._get_current_user),
        ) -> list[Source]:
            session = await self.session_store.get(session_id)
            if session is None or session.user_id != current_user.user_id:
                raise HTTPException(status_code=404, detail="Session not found")
            return await self.source_store.list_for_session(session_id)
