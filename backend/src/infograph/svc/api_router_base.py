"""Base API router for the Infograph service."""

from fastapi import APIRouter, Request


class APIRouterBase(APIRouter):
    """Base router that provides shared utilities."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_locale(self, request: Request) -> str:
        """Extract the preferred locale from the request."""
        accept_language = request.headers.get("accept-language", "en-US")
        return accept_language.split(",")[0].strip()
