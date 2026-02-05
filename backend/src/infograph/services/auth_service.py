"""Authentication helpers for Infograph."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import os
from typing import Any, Callable

import jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from infograph.core.schemas import User, UserCreate
from infograph.stores.abstract_user_store import AbstractUserStore


TokenVerifier = Callable[[str, str], dict[str, Any]]


@dataclass
class AuthSettings:
    jwt_secret: str
    google_client_id: str
    jwt_algorithm: str = "HS256"
    token_expiration_seconds: int = 86400


class AuthService:
    """Handle Google OAuth validation and JWT issuance."""

    def __init__(
        self,
        user_store: AbstractUserStore,
        token_verifier: TokenVerifier | None = None,
        settings: AuthSettings | None = None,
    ) -> None:
        self.user_store = user_store
        self.settings = settings or self._load_settings()
        self._token_verifier = token_verifier or self._default_token_verifier

    def _load_settings(self) -> AuthSettings:
        google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
        if not google_client_id:
            raise RuntimeError("GOOGLE_CLIENT_ID environment variable is not configured")

        jwt_secret = os.environ.get("JWT_SECRET")
        if not jwt_secret:
            raise RuntimeError("JWT_SECRET environment variable is not configured")

        return AuthSettings(jwt_secret=jwt_secret, google_client_id=google_client_id)

    def _default_token_verifier(self, credential: str, audience: str) -> dict[str, Any]:
        request = google_requests.Request()
        return id_token.verify_oauth2_token(
            credential,
            request,
            audience=audience,
        )

    async def authenticate(self, credential: str) -> tuple[User, str]:
        payload = self._token_verifier(credential, self.settings.google_client_id)
        email = payload.get("email")
        name = payload.get("name") or email
        google_id = payload.get("sub")

        if not email or not name or not google_id:
            raise ValueError("Google token payload missing required fields")

        user = await self.user_store.get_by_google_id(google_id)
        if user is None:
            user = await self.user_store.create(
                UserCreate(email=email, name=name, google_id=google_id)
            )

        token = jwt.encode(
            self._build_token_payload(user),
            self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
        )
        return user, token

    def _build_token_payload(self, user: User) -> dict[str, Any]:
        expiration = datetime.utcnow() + timedelta(seconds=self.settings.token_expiration_seconds)
        return {
            "user_id": user.user_id,
            "exp": int(expiration.timestamp()),
        }

    async def get_user_from_token(self, token: str) -> User:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm],
            )
        except jwt.PyJWTError as exc:
            raise ValueError("Invalid or expired token") from exc

        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("Token payload missing user_id")

        user = await self.user_store.get(user_id)
        if user is None:
            raise ValueError("User not found for token")

        return user

    async def refresh_user(self, google_id: str) -> User | None:
        return await self.user_store.get_by_google_id(google_id)
