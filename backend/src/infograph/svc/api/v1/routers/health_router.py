"""Health check router."""

from infograph.svc.api_router_base import APIRouterBase


class HealthRouter(APIRouterBase):
    """Router exposing system health endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        @self.get("/health")
        async def health_status() -> dict[str, str]:
            """Return a simple health response."""
            return {"status": "ok", "version": "1.0.0"}
