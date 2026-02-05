from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Query, status

from infograph.core.schemas import (
    Message,
    MessageCreate,
    ResearchSession,
    ResearchSessionCreate,
    User,
)
from infograph.services.auth_service import AuthService
from infograph.stores.abstract_message_store import AbstractMessageStore
from infograph.stores.abstract_session_store import AbstractSessionStore
from infograph.stores.duckdb.message_store_duckdb import MessageStoreDuckDB
from infograph.stores.duckdb.session_store_duckdb import SessionStoreDuckDB
from infograph.stores.duckdb.user_store_duckdb import UserStoreDuckDB
from infograph.svc.api_router_base import APIRouterBase


def _bearer_token_from_header(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")

    return parts[1]


class SessionRouter(APIRouterBase):
    """Router that exposes research session and message endpoints."""

    def __init__(
        self,
        *,
        session_store: AbstractSessionStore | None = None,
        message_store: AbstractMessageStore | None = None,
        auth_service: AuthService | None = None,
    ) -> None:
        super().__init__()
        self.session_store = session_store or SessionStoreDuckDB()
        self.message_store = message_store or MessageStoreDuckDB()
        self.auth_service = auth_service or AuthService(user_store=UserStoreDuckDB())
        self._register_routes()

    def _register_routes(self) -> None:
        @self.post("", response_model=ResearchSession, status_code=status.HTTP_201_CREATED)
        async def create_session(
            payload: ResearchSessionCreate,
            user: User = Depends(self._get_current_user),
        ) -> ResearchSession:
            return await self.session_store.create(payload, user.user_id)

        @self.get("", response_model=list[ResearchSession])
        async def list_sessions(
            limit: int = Query(10, ge=1, le=100),
            offset: int = Query(0, ge=0),
            user: User = Depends(self._get_current_user),
        ) -> list[ResearchSession]:
            sessions = list(await self.session_store.list_for_user(user.user_id))
            return sessions[offset : offset + limit]

        @self.get("/{session_id}", response_model=ResearchSession)
        async def get_session(
            session_id: str,
            user: User = Depends(self._get_current_user),
        ) -> ResearchSession:
            return await self._ensure_session_access(session_id, user.user_id)

        @self.delete("/{session_id}")
        async def delete_session(
            session_id: str,
            user: User = Depends(self._get_current_user),
        ) -> dict[str, bool]:
            await self._ensure_session_access(session_id, user.user_id)
            await self.session_store.delete(session_id)
            return {"success": True}

        @self.post("/{session_id}/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
        async def create_message(
            session_id: str,
            payload: MessageCreate,
            user: User = Depends(self._get_current_user),
        ) -> Message:
            if payload.session_id != session_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payload session_id does not match URL",
                )
            await self._ensure_session_access(session_id, user.user_id)
            return await self.message_store.create(payload)

        @self.get("/{session_id}/messages", response_model=list[Message])
        async def list_messages(
            session_id: str,
            user: User = Depends(self._get_current_user),
        ) -> list[Message]:
            await self._ensure_session_access(session_id, user.user_id)
            return await self.message_store.list_for_session(session_id)

    async def _get_current_user(self, authorization: str | None = Header(None, alias="Authorization")) -> User:
        token = _bearer_token_from_header(authorization)
        try:
            return await self.auth_service.get_user_from_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    async def _ensure_session_access(self, session_id: str, user_id: str) -> ResearchSession:
        session = await self.session_store.get(session_id)
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        if session.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this session")
        return session
