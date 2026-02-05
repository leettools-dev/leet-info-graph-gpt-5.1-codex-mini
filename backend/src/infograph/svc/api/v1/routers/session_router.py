"""Router for research session management."""

from __future__ import annotations

from typing import Iterable

from fastapi import Depends, Header, HTTPException

from infograph.core.schemas import ResearchSession, ResearchSessionCreate, User
from infograph.services.auth_service import AuthService
from infograph.stores.duckdb.session_store_duckdb import SessionStoreDuckDB
from infograph.stores.duckdb.user_store_duckdb import UserStoreDuckDB
from infograph.stores.abstract_user_store import AbstractUserStore
from infograph.stores.abstract_session_store import AbstractSessionStore
from infograph.svc.api_router_base import APIRouterBase


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    return parts[1]


class SessionRouter(APIRouterBase):
    """Router exposing CRUD operations for research sessions."""

    def __init__(
        self,
        *,
        session_store: AbstractSessionStore | None = None,
        user_store: AbstractUserStore | None = None,
        auth_service: AuthService | None = None,
    ) -> None:
        super().__init__()
        self.session_store = session_store or SessionStoreDuckDB()
        self.user_store = user_store or UserStoreDuckDB(self.session_store.settings)
        self.auth_service = auth_service or AuthService(self.user_store)
        self._register_routes()

    async def _get_current_user(
        self,
        authorization: str | None = Header(None, alias="Authorization"),
    ) -> User:
        """Resolve the current user from a bearer token."""
        token = _extract_bearer_token(authorization)
        try:
            return await self.auth_service.get_user_from_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    def _register_routes(self) -> None:

        @self.post("", response_model=ResearchSession, status_code=201)
        async def create_session(
            payload: ResearchSessionCreate,
            current_user: User = Depends(self._get_current_user),
        ) -> ResearchSession:
            """Create a new research session for the authenticated user."""
            return await self.session_store.create(payload, current_user.user_id)

        @self.get("", response_model=list[ResearchSession])
        async def list_sessions(
            current_user: User = Depends(self._get_current_user),
        ) -> list[ResearchSession]:
            """List research sessions belonging to the authenticated user."""
            sessions: Iterable[ResearchSession] = await self.session_store.list_for_user(
                current_user.user_id
            )
            return list(sessions)

        @self.get("/{session_id}", response_model=ResearchSession)
        async def get_session(
            session_id: str,
            current_user: User = Depends(self._get_current_user),
        ) -> ResearchSession:
            """Fetch a session by ID if it belongs to the user."""
            session = await self.session_store.get(session_id)
            if session is None or session.user_id != current_user.user_id:
                raise HTTPException(status_code=404, detail="Session not found")
            return session

        @self.delete("/{session_id}")
        async def delete_session(
            session_id: str,
            current_user: User = Depends(self._get_current_user),
        ) -> dict[str, bool]:
            """Delete a session that belongs to the calling user."""
            session = await self.session_store.get(session_id)
            if session is None or session.user_id != current_user.user_id:
                raise HTTPException(status_code=404, detail="Session not found")

            await self.session_store.delete(session_id)
            return {"success": True}
