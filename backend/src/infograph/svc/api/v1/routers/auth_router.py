"""Authentication router for Infograph service."""

from __future__ import annotations

from fastapi import Header, HTTPException
from pydantic import BaseModel

from infograph.core.schemas import User
from infograph.services.auth_service import AuthService
from infograph.stores.abstract_user_store import AbstractUserStore
from infograph.stores.duckdb.user_store_duckdb import UserStoreDuckDB
from infograph.svc.api_router_base import APIRouterBase


class GoogleAuthRequest(BaseModel):
    """Request body for exchanging a Google credential."""

    credential: str


class AuthResponse(BaseModel):
    """Response returned after successful authentication."""

    user: User
    token: str


def _bearer_token_from_header(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    return parts[1]


class AuthRouter(APIRouterBase):
    """Router that exposes authentication endpoints."""

    def __init__(
        self,
        *,
        user_store: AbstractUserStore | None = None,
        auth_service: AuthService | None = None,
    ) -> None:
        super().__init__()
        self.user_store = user_store or UserStoreDuckDB()
        self.auth_service = auth_service or AuthService(self.user_store)
        self._register_routes()

    def _register_routes(self) -> None:
        @self.post("/google", response_model=AuthResponse)
        async def google_sign_in(payload: GoogleAuthRequest) -> AuthResponse:
            user, token = await self.auth_service.authenticate(payload.credential)
            return AuthResponse(user=user, token=token)

        @self.get("/me", response_model=User)
        async def get_current_user(
            authorization: str | None = Header(None, alias="Authorization")
        ) -> User:
            token = _bearer_token_from_header(authorization)
            return await self.auth_service.get_user_from_token(token)

        @self.post("/logout")
        async def logout() -> dict[str, bool]:
            return {"success": True}
