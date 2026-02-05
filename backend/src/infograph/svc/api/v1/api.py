"""API router aggregator for version 1 endpoints."""

from fastapi import APIRouter

from infograph.svc.api.v1.routers import health_router, auth_router


class ServiceAPIRouter(APIRouter):
    """Aggregate router for all v1 endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.health_router = health_router.HealthRouter()
        super().include_router(
            self.health_router,
            prefix="",
            tags=["health"],
        )

        self.auth_router = auth_router.AuthRouter()
        super().include_router(
            self.auth_router,
            prefix="/api/v1/auth",
            tags=["auth"],
        )
